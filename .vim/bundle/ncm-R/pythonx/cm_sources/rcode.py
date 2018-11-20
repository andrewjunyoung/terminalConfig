# -*- coding: utf-8 -*-
"""
R Source for Neovim Completion Manager, to be used with nvim-R

by Gabriel Alcaras
"""

from os import listdir, path
import re

from neovim.api.nvim import NvimError
from cm import register_source  # pylint: disable=E0401

from rsource import Rsource  # pylint: disable=E0401
import filtr  # pylint: disable=E0401
import rlang  # pylint: disable=E0401

register_source(name='R',
                priority=9,
                abbreviation='R',
                word_pattern=r'[\w_\.]+',
                scoping=True,
                scopes=['r'],
                sort=0,
                early_cache=1,
                cm_refresh_patterns=[
                    r'\$', r'::', r'"', r"'",
                    # Refresh immediately after symbol and after typing 3 chars
                    r',\s([\w_\.]{3})?',  # New argument
                    r'^\s{2,}([\w_\.]{3})?$',  # New argument on a new line
                    r'\(([\w_\.]{3})?',  # After a parenthesis
                ])


class Source(Rsource):  # pylint: disable=R0902
    """Completion Manager Source for R language"""

    R_WORD = re.compile(r'[\w\$_\.]+$')

    def __init__(self, nvim):
        super(Source, self).__init__(nvim)

        self._pkg_loaded = list()
        self._pkg_installed = list()

        self._all_matches = list()
        self._pkg_matches = list()
        self._fnc_matches = list()
        self._obj_matches = list()

    def cm_setup(self):
        """Set up Source settings"""

        try:
            self._settings['nvimr'] = self.nvim.eval('$NVIMR_ID')
            self._settings['tmpdir'] = self.nvim.eval('g:rplugin_tmpdir')
            self._settings['cmpdir'] = self.nvim.eval('g:rplugin_compldir')
        except NvimError:
            self._error('Can\'t load Nvim-R options. '
                        'Did you install the Nvim-R plugin?')
            raise

        self.get_all_pkg_matches()

    def update_loaded_pkgs(self):
        """Update list of loaded R packages

        :returns: 1 if loaded packages have changed, 0 otherwise
        """

        old_pkgs = self._pkg_loaded[:]

        try:
            pkg_loaded = self.nvim.eval('g:rplugin_loaded_libs')
            self._pkg_loaded = list(reversed(pkg_loaded))
        except NvimError:
            self._error('Can\'t find loaded R packages. '
                        'Please start R using Nvim-R '
                        '(default mapping: <localleader>rf).')
            raise

        new_loaded_pkgs = (set(old_pkgs) != set(self._pkg_loaded))
        new_pkgs = any(p not in self._pkg_installed for p in self._pkg_loaded)

        if not new_loaded_pkgs and not new_pkgs and self._pkg_installed:
            return 0

        if not self._pkg_installed:
            self.get_all_pkg_matches()

        if new_pkgs:
            self._info('Some loaded packages miss an omni file. '
                       'Refreshing matches...')
            self.get_all_pkg_matches()

        return 1

    def get_all_obj_matches(self):
        """Populate candidates with all R objects in the environment"""

        globenv_file = path.join(self._settings['tmpdir'],
                                 'GlobalEnvList_' + self._settings['nvimr'])

        with open(globenv_file, 'r') as globenv:
            objs = [obj.strip() for obj in globenv.readlines()]

        self._obj_matches = self.matches.from_omnils(objs)

    def get_all_pkg_matches(self):
        """Populate matches list with candidates from every R package"""

        cmpdir = self._settings['cmpdir']

        try:
            comps = [f for f in listdir(cmpdir) if 'omnils' in f]

            if not comps:
                raise FileNotFoundError('Could not find any omnils_* files '
                                        'in {}.'.format(cmpdir))

            for filename in comps:
                pkg_name = re.search(r'_(.*)_', filename).group(1)

                if pkg_name in self._pkg_installed:
                    continue

                self._pkg_installed.append(pkg_name)

                filepath = path.join(self._settings['cmpdir'], filename)

                with open(filepath, 'r') as omnil:
                    comps = [pkg.strip() for pkg in omnil.readlines()]

                self._all_matches.extend(self.matches.from_omnils(comps))

            pkg_desc = path.join(cmpdir, 'pack_descriptions')

            with open(pkg_desc, 'r') as desc:
                descriptions = [pkg.strip() for pkg in desc.readlines()]

            self._pkg_matches.extend(self.matches.from_pkg_desc(descriptions))
        except FileNotFoundError:
            self._error('Can\'t find completion files. Please load the '
                        'R packages you need (e.g. "base" or "utils").')
            raise
        except Exception as error:
            self._error('Could not load completion data', error)
            raise

    def get_data_matches(self):
        """Return list of matches with datasets from R packages"""

        pkg_matches = filtr.pkg(self._all_matches, self._pkg_loaded)
        data = filtr.struct(pkg_matches, 'data.frame')
        data.extend(filtr.struct(pkg_matches, 'tbl_df'))

        return data

    def update_func_matches(self):
        """Update function matches if necessary"""

        if self.update_loaded_pkgs():
            self._info('Update loaded R packages: %s', self._pkg_loaded)
            funcs = filtr.pkg(self._all_matches, self._pkg_loaded)
            funcs = filtr.struct(funcs, 'function')
            self._fnc_matches = funcs

    def get_matches(self, word, pkg=None, pipe=None):
        """Return function and object matches based on given word

        :word: string to filter matches with
        :pkg: only show functions from R package
        :pipe: piped data
        :returns: list of ncm matches
        """

        self.get_all_obj_matches()
        obj_m = self._obj_matches

        if pipe:
            # Inside data pipeline, keep variables from piped data
            obj_m = filtr.word(obj_m, pipe + '$', rm_typed=True)
        else:
            if '$' in word:
                # If we're looking inside a data frame or tibble, only return
                # its variables
                obj_m = filtr.word(obj_m, word, rm_typed=True)
            else:
                # Otherwise, hide what's inside data.frames
                obj_m = filtr.word(obj_m, word, hide='$')

        matches = obj_m

        # Get functions from loaded R packages
        self.update_func_matches()
        func_m = filtr.pkg(self._fnc_matches, pkg)
        func_m.extend(self._pkg_matches)

        if not pkg or (pkg and word):
            func_m = filtr.word(func_m, word)

        matches.extend(func_m)

        return matches

    def get_func_matches(self, func, word, pipe=None):
        """Return matches when completion happens inside function

        :func: the name of function
        :word: word typed
        :pipe: piped data
        :returns: list of ncm matches
        """

        if func in ('library', 'require'):
            return self._pkg_matches

        if func in 'data':
            return self.get_data_matches()

        args = list()
        for matches in [self._fnc_matches, self._obj_matches]:
            tmp_args = filtr.arg(matches, func, pipe)
            args.extend(tmp_args)

            if len(args) > 1:
                break

        objs = self.get_matches(word, pipe=pipe)

        matches = list()
        if pipe:
            matches.extend(objs+args)
        else:
            matches.extend(args+objs)

        return matches

    def cm_refresh(self, info, ctx,):
        """Refresh NCM list of matches"""

        cur_buffer = self.nvim.current.buffer
        lnum = ctx['lnum']
        col = ctx['col']

        if ctx['filetype'] in ('rnoweb', 'rmd'):
            cur_buffer = cur_buffer[ctx['scope_lnum']-1:]

        if re.match('^#', cur_buffer[lnum-1]):
            return

        word_match = re.search(self.R_WORD, ctx['typed'])
        word = word_match.group(0) if word_match else ''

        isinquot = re.search('["\']' + word + '$', ctx['typed'])

        function = rlang.get_function(cur_buffer, lnum, col)
        pkg = function[0]
        func = function[1]

        if isinquot and func and not re.search('(library|require|data)', func):
            return

        pipe = rlang.get_pipe(cur_buffer, lnum, col)

        self._info('word: "{}", func: "{}", pkg: {}, pipe: {}'.format(
            word, func, pkg, pipe))

        if func:
            matches = self.get_func_matches(func, word, pipe)
        else:
            if not word and not pkg:
                return

            matches = self.get_matches(word, pkg=pkg)

        self.complete(info, ctx, ctx['startcol'], matches)
