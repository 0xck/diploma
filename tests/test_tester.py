import sys
import os
import json
import gc
from unittest import TestCase, skip
from stuff import combination_dicts, str_cutter
# adding paths
CURR_PATH = os.path.abspath(os.path.dirname('__file__'))
PARENT_PATH = os.path.abspath(os.path.join(CURR_PATH, os.pardir))
sys.path.insert(0, PARENT_PATH)

from trex.tester import Tester
from trex.helper import TREXMODE
from trex.client import TRexClientWrapper, TRexSTLClientWrapper
from trex.exceptions import TRexClientWrapperError, TRexSTLClientWrapperError

TREX_STF = os.path.abspath(os.path.join(CURR_PATH, './trex_stuff/stf'))
TREX_STL = os.path.abspath(os.path.join(CURR_PATH, './trex_stuff/stl'))


class CreateTesterTest(TestCase):

    @skip
    def test_create_default(self):

        for i in TREXMODE:
            with self.subTest(i=i):
                t = Tester(mode=i.value)
                self.assertEqual(t.mode, i)
                self.assertIsInstance(t.server, TRexClientWrapper)
                if i == TREXMODE.stf:
                    self.assertIsInstance(t.client, TRexClientWrapper)
                elif i == TREXMODE.stl:
                    self.assertIsInstance(t.client, TRexSTLClientWrapper)

        print('ID t', id(t))

    @skip
    def test_create_server_from_json(self):
        with open(os.path.join(TREX_STF, 'srv_default.json'), 'r', encoding='utf-8') as f:
            cfg = combination_dicts(json.load(f))

        for c in cfg:
            with self.subTest(c=c):
                for i in TREXMODE:
                    with self.subTest(i=i):
                        t = Tester(server=c, mode=i.value)
                        self.assertIsInstance(t.server, TRexClientWrapper)

        print('ID t', id(t))

    @skip
    def test_create_server_from_json_bad_keys(self):
        # only valid keys are updated
        with open(os.path.join(TREX_STF, 'srv_default.json'), 'r', encoding='utf-8') as f:
            cfg = combination_dicts({str_cutter(k): v for k, v in json.load(f).items()})

        for c in cfg:
            with self.subTest(c=c):
                for i in TREXMODE:
                    with self.subTest(i=i):
                        t = Tester(server=c, mode=i.value)
                        self.assertIsInstance(t.server, TRexClientWrapper)

        print('ID t', id(t))

    @skip
    def test_create_stf_test_from_json(self):
        with open(os.path.join(TREX_STF, 'test_default.json'), 'r', encoding='utf-8') as f:
            cfg = combination_dicts(json.load(f))

        for c in cfg:
            with self.subTest(c=c):
                t = Tester(test=c, mode=TREXMODE.stf.value)
                self.assertIsInstance(t.server, TRexClientWrapper)
                self.assertIsInstance(t.client, TRexClientWrapper)

        print('ID t', id(t))

    #@skip
    def test_create_stf_test_from_json_bad_keys(self):
        # nothing until start test
        with open(os.path.join(TREX_STF, 'test_default.json'), 'r', encoding='utf-8') as f:
            cfg = combination_dicts({str_cutter(k): v for k, v in json.load(f).items()})

        for c in cfg:
            with self.subTest(c=c):
                t = Tester(test=c, mode=TREXMODE.stf.value)
                self.assertIsInstance(t.server, TRexClientWrapper)
                self.assertIsInstance(t.client, TRexClientWrapper)

        print('ID t', id(t))

    @skip
    def test_create_stl_test_from_json(self):
        with open(os.path.join(TREX_STL, 'client_default.json'), 'r', encoding='utf-8') as f:
            client = json.load(f)
        with open(os.path.join(TREX_STL, 'test_default.json'), 'r', encoding='utf-8') as f:
            test = (json.load(f))

        client.update(test)

        cfg = combination_dicts(client)

        for c in cfg:
            with self.subTest(c=c):
                t = Tester(test=c, mode=TREXMODE.stl.value)
                self.assertIsInstance(t.server, TRexClientWrapper)
                self.assertIsInstance(t.client, TRexSTLClientWrapper)

        print('ID t', id(t))

    @skip
    def test_create_stl_test_from_json_bad_keys(self):
        with open(os.path.join(TREX_STL, 'client_default.json'), 'r', encoding='utf-8') as f:
            client = {str_cutter(k): v for k, v in json.load(f).items()}
        with open(os.path.join(TREX_STL, 'test_default.json'), 'r', encoding='utf-8') as f:
            test = {str_cutter(k): v for k, v in json.load(f).items()}

        client.update(test)

        cfg = combination_dicts(client)

        for c in cfg:
            with self.subTest(c=c):
                t = Tester(test=c, mode=TREXMODE.stl.value)
                self.assertIsInstance(t.server, TRexClientWrapper)
                self.assertIsInstance(t.client, TRexSTLClientWrapper)

        print('ID t', id(t))

    def test_run_stf_real_from_json(self):


        with open(os.path.join(TREX_STF, 'test_default.json'), 'r', encoding='utf-8') as f:
            cfg = json.load(f)


        x = Tester(mode=TREXMODE.stf.value, test=cfg)

        print('ID t', id(x))
        
        raise ValueError('\n'.join((str(x.show_cfg()), str(cfg))))

        self.assertTrue(x.run_loop())

