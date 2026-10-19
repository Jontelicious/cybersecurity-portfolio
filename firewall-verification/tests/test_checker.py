import io
import json
from pathlib import Path
import socket
import sys
import threading
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_firewall as checker

class CheckerTests(unittest.TestCase):
    def test_timeout_is_not_a_confirmed_block(self):
        result=checker.classify_tcp({'observed':'timeout'},'block')
        self.assertEqual(result['status'],'NEEDS_ROUTER_EVIDENCE')
        self.assertEqual(checker.exit_status({'tests':[result]}),2)

    def test_refusal_is_not_a_confirmed_block(self):
        self.assertEqual(checker.classify_tcp({'observed':'socket_error'},'block')['status'],'NEEDS_ROUTER_EVIDENCE')

    def test_unexpected_connection_fails_isolation(self):
        result=checker.classify_tcp({'observed':'connected'},'block')
        self.assertEqual(result['status'],'FAIL')
        self.assertEqual(checker.exit_status({'tests':[result]}),1)

    def test_real_loopback_positive_control(self):
        with socket.socket() as listener:
            listener.bind(('127.0.0.1',0));listener.listen()
            thread=threading.Thread(target=lambda: listener.accept()[0].close())
            thread.start()
            result=checker.tcp_probe('127.0.0.1','127.0.0.1',listener.getsockname()[1])
            thread.join(timeout=3)
            self.assertEqual(result['observed'],'connected')

    def test_dns_servfail_or_wrong_server_does_not_pass(self):
        answer='example.com. 60 IN A 192.0.2.1\n;; SERVER: 10.1.10.254#53\n'
        good=dict(exit_code=0,stdout='status: NOERROR\n'+answer)
        self.assertTrue(checker.dns_ok(good,'10.1.10.254'))
        self.assertFalse(checker.dns_ok(dict(exit_code=0,stdout='status: SERVFAIL\n'+answer),'10.1.10.254'))
        self.assertFalse(checker.dns_ok(good,'10.1.20.254'))

    def test_wrong_machine_skips_network_probes(self):
        with patch.object(checker,'command',return_value=dict(exit_code=0,stdout='[]')),patch.object(checker,'tcp_probe',side_effect=AssertionError('must not probe')):
            result=checker.collect('client1')
        self.assertIn('setup_error',result)
        self.assertEqual(result['tests'],[])

    def test_output_path_errors_skip_probes_and_preserve_existing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            existing = Path(folder) / 'existing.json'
            existing.write_text('original report\n')
            paths = (existing, Path(folder) / 'missing' / 'report.json')
            for output in paths:
                with self.subTest(output=output):
                    stderr = io.StringIO()
                    with patch.object(sys, 'argv', ['check_firewall.py', '--node',
                                      'client1', '--output', str(output)]), \
                         patch.object(sys, 'stderr', stderr), \
                         patch.object(checker, 'collect') as collect:
                        self.assertEqual(checker.main(), 2)
                    collect.assert_not_called()
                    self.assertIn('Setup error: cannot create output file', stderr.getvalue())
                    self.assertNotIn('Traceback', stderr.getvalue())
                    self.assertEqual(len(stderr.getvalue().splitlines()), 1)
            self.assertEqual(existing.read_text(), 'original report\n')
            self.assertFalse(paths[1].exists())

    def test_complete_client_run_separates_manual_evidence(self):
        def fake(argv,timeout):
            if argv[0]=='ip' and 'addr' in argv:
                return dict(exit_code=0,stdout=json.dumps([{'addr_info':[{'local':'10.1.10.10'}]}]))
            if argv[0]=='ip':
                return dict(exit_code=0,stdout=json.dumps([{'gateway':'10.1.10.254'}]))
            if argv[0]=='dig':
                return dict(exit_code=0,stdout='status: NOERROR\nexample.com. 60 IN A 192.0.2.1\n;; SERVER: 10.1.10.254#53\n')
            return dict(exit_code=0,stdout='HTTP/2 200\nHTTP_STATUS=200\n')
        def tcp(source,destination):
            return dict(observed='timeout' if destination=='10.1.30.10' else 'connected')
        with patch.object(checker,'command',side_effect=fake),patch.object(checker,'tcp_probe',side_effect=tcp):
            result=checker.collect('client1')
        self.assertEqual(len(result['tests']),6)
        self.assertEqual(checker.exit_status(result),2)
        self.assertEqual([x['status'] for x in result['tests']].count('NEEDS_ROUTER_EVIDENCE'),1)

if __name__=='__main__': unittest.main()
