import os
import re
import unittest
from click.testing import CliRunner
from metapool.scripts.seqpro import format_preparation_files
from shutil import copy, copytree, rmtree
from os.path import join
from subprocess import Popen, PIPE
import pandas as pd


class SeqproTests(unittest.TestCase):
    def setUp(self):
        # we need to get the test data directory in the parent directory
        # important to use abspath because we use CliRunner.isolated_filesystem
        tests_dir = os.path.abspath(os.path.dirname(__file__))
        tests_dir = os.path.dirname(os.path.dirname(tests_dir))
        self.test_dir = os.path.join(tests_dir, 'tests')
        data_dir = os.path.join(self.test_dir, 'data')
        self.vf_test_dir = os.path.join(tests_dir, 'tests', 'VFTEST')

        self.run = os.path.join(data_dir, 'runs',
                                '191103_D32611_0365_G00DHB5YXX')
        self.sheet = os.path.join(self.run, 'sample-sheet.csv')

        self.fastp_run = os.path.join(data_dir, 'runs',
                                      '200318_A00953_0082_AH5TWYDSXY')
        self.fastp_sheet = os.path.join(self.fastp_run, 'sample-sheet.csv')

    def tearDown(self):
        rmtree(self.vf_test_dir, ignore_errors=True)

    def test_atropos_run(self):
        # TODO: Fix this test
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(format_preparation_files,
                                   args=[self.run, self.sheet, './',
                                         '--pipeline', 'atropos-and-bowtie2'])

            # assert that expected error message appeared in stdout. we are
            # not concerned w/warning messages that may also appear.
            self.assertIn('Stats collection is not supported for pipeline '
                          'atropos-and-bowtie2', result.output)
            self.assertEqual(result.exit_code, 0)

            exp_preps = [
                '191103_D32611_0365_G00DHB5YXX.Baz_12345.1.tsv',
                '191103_D32611_0365_G00DHB5YXX.Baz_12345.3.tsv',
                '191103_D32611_0365_G00DHB5YXX.FooBar_666.3.tsv'
            ]

            self.assertEqual(sorted(os.listdir('./')), exp_preps)

            for prep, exp_lines in zip(exp_preps, [4, 4, 5]):
                with open(prep) as f:
                    self.assertEqual(len(f.read().split('\n')),
                                     exp_lines,
                                     'Assertion error in %s' % prep)

    def test_fastp_run(self):
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(format_preparation_files,
                                   args=[self.fastp_run, self.fastp_sheet,
                                         './', '--pipeline',
                                         'fastp-and-minimap2'])

            self.assertEqual(result.output, '')
            self.assertEqual(result.exit_code, 0)

            exp_preps = [
                '200318_A00953_0082_AH5TWYDSXY.Project_1111.1.tsv',
                '200318_A00953_0082_AH5TWYDSXY.Project_1111.3.tsv',
                '200318_A00953_0082_AH5TWYDSXY.Trojecp_666.3.tsv'
            ]

            # assert filenames are correct, and contents are correct,
            # including columns, column order, and empty values are not
            # present.
            exp = {'200318_A00953_0082_AH5TWYDSXY.Project_1111.1.tsv': {
                0: {'experiment_design_description': 'Eqiiperiment',
                    'well_description': 'FooBar_666_p1.sample1.A1',
                    'library_construction_protocol': 'Knight Lab Kapa HP',
                    'platform': 'Illumina', 'run_center': 'IGM',
                    'run_date': '2020-03-18',
                    'run_prefix': 'sample1_S333_L001',
                    'sequencing_meth': 'sequencing by synthesis',
                    'center_name': 'UCSD', 'center_project_name': 'Project',
                    'instrument_model': 'Illumina NovaSeq 6000',
                    'runid': '200318_A00953_0082_AH5TWYDSXY', 'lane': 1,
                    'sample_project': 'Project', 'i5_index_id': 'iTru5_01_A',
                    'index2': 'ACCGACAA', 'sample_plate': 'FooBar_666_p1',
                    'well_id_384': 'A1', 'sample_name': 'sample1',
                    'index': 'CCGACTAT', 'i7_index_id': 'iTru7_107_07',
                    'raw_reads_r1r2': 10000,
                    'quality_filtered_reads_r1r2': 16.0,
                    'total_biological_reads_r1r2': 10800.0,
                    'non_host_reads': 111172.0,
                    'fraction_passing_quality_filter': 0.0016,
                    # although the below value appears non-sensical, it is
                    # expected due to the value of non-host reads found in
                    # the sample samtools log files and the actual number of
                    # sequences found in the test fastq files.
                    'fraction_non_human': 6948.25},
                1: {'experiment_design_description': 'Eqiiperiment',
                    'well_description': 'FooBar_666_p1.sample2.A2',
                    'library_construction_protocol': 'Knight Lab Kapa HP',
                    'platform': 'Illumina', 'run_center': 'IGM',
                    'run_date': '2020-03-18',
                    'run_prefix': 'sample2_S404_L001',
                    'sequencing_meth': 'sequencing by synthesis',
                    'center_name': 'UCSD', 'center_project_name': 'Project',
                    'instrument_model': 'Illumina NovaSeq 6000',
                    'runid': '200318_A00953_0082_AH5TWYDSXY', 'lane': 1,
                    'sample_project': 'Project', 'i5_index_id': 'iTru5_01_A',
                    'index2': 'CTTCGCAA', 'sample_plate': 'FooBar_666_p1',
                    'well_id_384': 'A2', 'sample_name': 'sample2',
                    'index': 'CCGACTAT', 'i7_index_id': 'iTru7_107_08',
                    'raw_reads_r1r2': 100000,
                    'quality_filtered_reads_r1r2': 16.0,
                    'total_biological_reads_r1r2': 61404.0,
                    'non_host_reads': 277611.0,
                    'fraction_passing_quality_filter': 0.00016,
                    # although the below value appears non-sensical, it is
                    # expected due to the value of non-host reads found in
                    # the sample samtools log files and the actual number of
                    # sequences found in the test fastq files.
                    'fraction_non_human': 17350.6875}},
                   '200318_A00953_0082_AH5TWYDSXY.Project_1111.3.tsv': {
                0: {'experiment_design_description': 'Eqiiperiment',
                    'well_description': 'FooBar_666_p1.sample1.A3',
                    'library_construction_protocol': 'Knight Lab Kapa HP',
                    'platform': 'Illumina', 'run_center': 'IGM',
                    'run_date': '2020-03-18',
                    'run_prefix': 'sample1_S241_L003',
                    'sequencing_meth': 'sequencing by synthesis',
                    'center_name': 'UCSD', 'center_project_name': 'Project',
                    'instrument_model': 'Illumina NovaSeq 6000',
                    'runid': '200318_A00953_0082_AH5TWYDSXY', 'lane': 3,
                    'sample_project': 'Project',
                    'i5_index_id': 'iTru5_01_A', 'index2': 'AACACCAC',
                    'sample_plate': 'FooBar_666_p1',
                    'well_id_384': 'A3', 'sample_name': 'sample1',
                    'index': 'GCCTTGTT', 'i7_index_id': 'iTru7_107_09',
                    'raw_reads_r1r2': 100000,
                    'quality_filtered_reads_r1r2': 16.0,
                    'total_biological_reads_r1r2': 335996.0,
                    'non_host_reads': 1168275.0,
                    'fraction_passing_quality_filter': 0.00016,
                    'fraction_non_human': 73017.1875},
                1: {'experiment_design_description': 'Eqiiperiment',
                    'well_description': 'FooBar_666_p1.sample2.A4',
                    'library_construction_protocol': 'Knight Lab Kapa HP',
                    'platform': 'Illumina', 'run_center': 'IGM',
                    'run_date': '2020-03-18',
                    'run_prefix': 'sample2_S316_L003',
                    'sequencing_meth': 'sequencing by synthesis',
                    'center_name': 'UCSD',
                    'center_project_name': 'Project',
                    'instrument_model': 'Illumina NovaSeq 6000',
                    'runid': '200318_A00953_0082_AH5TWYDSXY', 'lane': 3,
                    'sample_project': 'Project',
                    'i5_index_id': 'iTru5_01_A', 'index2': 'CGTATCTC',
                    'sample_plate': 'FooBar_666_p1',
                    'well_id_384': 'A4', 'sample_name': 'sample2',
                    'index': 'AACTTGCC', 'i7_index_id': 'iTru7_107_10',
                    'raw_reads_r1r2': 2300000,
                    'quality_filtered_reads_r1r2': 16.0,
                    'total_biological_reads_r1r2': 18374.0,
                    'non_host_reads': 1277.0,
                    'fraction_passing_quality_filter': 0.000006956521739130435,
                    'fraction_non_human': 79.8125}},
                   '200318_A00953_0082_AH5TWYDSXY.Trojecp_666.3.tsv': {
                0: {'experiment_design_description': 'SomethingWitty',
                    'well_description': 'FooBar_666_p1.sample3.A5',
                    'library_construction_protocol': 'Knight Lab Kapa HP',
                    'platform': 'Illumina', 'run_center': 'IGM',
                    'run_date': '2020-03-18',
                    'run_prefix': 'sample3_S457_L003',
                    'sequencing_meth': 'sequencing by synthesis',
                    'center_name': 'UCSD',
                    'center_project_name': 'Trojecp',
                    'instrument_model': 'Illumina NovaSeq 6000',
                    'runid': '200318_A00953_0082_AH5TWYDSXY', 'lane': 3,
                    'sample_project': 'Trojecp',
                    'i5_index_id': 'iTru5_01_A', 'index2': 'GGTACGAA',
                    'sample_plate': 'FooBar_666_p1',
                    'well_id_384': 'A5', 'sample_name': 'sample3',
                    'index': 'CAATGTGG', 'i7_index_id': 'iTru7_107_11',
                    'raw_reads_r1r2': 300000,
                    'quality_filtered_reads_r1r2': 16.0,
                    'total_biological_reads_r1r2': 4692.0,
                    'non_host_reads': 33162.0,
                    'fraction_passing_quality_filter': 0.00005333333333333333,
                    'fraction_non_human': 2072.625},
                1: {'experiment_design_description': 'SomethingWitty',
                    'well_description': 'FooBar_666_p1.sample4.B6',
                    'library_construction_protocol': 'Knight Lab Kapa HP',
                    'platform': 'Illumina', 'run_center': 'IGM',
                    'run_date': '2020-03-18',
                    'run_prefix': 'sample4_S369_L003',
                    'sequencing_meth': 'sequencing by synthesis',
                    'center_name': 'UCSD',
                    'center_project_name': 'Trojecp',
                    'instrument_model': 'Illumina NovaSeq 6000',
                    'runid': '200318_A00953_0082_AH5TWYDSXY', 'lane': 3,
                    'sample_project': 'Trojecp',
                    'i5_index_id': 'iTru5_01_A', 'index2': 'CGATCGAT',
                    'sample_plate': 'FooBar_666_p1',
                    'well_id_384': 'B6', 'sample_name': 'sample4',
                    'index': 'AAGGCTGA', 'i7_index_id': 'iTru7_107_12',
                    'raw_reads_r1r2': 400000,
                    'quality_filtered_reads_r1r2': 16.0,
                    'total_biological_reads_r1r2': 960.0,
                    'non_host_reads': 2777.0,
                    'fraction_passing_quality_filter': 0.00004,
                    'fraction_non_human': 173.5625},
                2: {'experiment_design_description': 'SomethingWitty',
                    'well_description': 'FooBar_666_p1.sample5.B8',
                    'library_construction_protocol': 'Knight Lab Kapa HP',
                    'platform': 'Illumina', 'run_center': 'IGM',
                    'run_date': '2020-03-18',
                    'run_prefix': 'sample5_S392_L003',
                    'sequencing_meth': 'sequencing by synthesis',
                    'center_name': 'UCSD',
                    'center_project_name': 'Trojecp',
                    'instrument_model': 'Illumina NovaSeq 6000',
                    'runid': '200318_A00953_0082_AH5TWYDSXY', 'lane': 3,
                    'sample_project': 'Trojecp',
                    'i5_index_id': 'iTru5_01_A', 'index2': 'AAGACACC',
                    'sample_plate': 'FooBar_666_p1',
                    'well_id_384': 'B8', 'sample_name': 'sample5',
                    'index': 'TTACCGAG', 'i7_index_id': 'iTru7_107_13',
                    'raw_reads_r1r2': 567000,
                    'quality_filtered_reads_r1r2': 16.0,
                    'total_biological_reads_r1r2': 30846196.0,
                    'non_host_reads': 4337654.0,
                    'fraction_passing_quality_filter': 0.000028218694885361552,
                    'fraction_non_human': 271103.375}}
                   }

            for prep in exp_preps:
                obs = pd.read_csv(prep, sep='\t').to_dict('index')
                self.assertDictEqual(obs, exp[prep])

    def test_verbose_flag(self):
        self.maxDiff = None
        sample_dir = 'metapool/tests/data/runs/200318_A00953_0082_AH5TWYDSXY'

        cmd = ['seqpro', '--verbose',
               sample_dir,
               join(sample_dir, 'sample-sheet.csv'),
               self.vf_test_dir]

        proc = Popen(' '.join(cmd), universal_newlines=True, shell=True,
                     stdout=PIPE, stderr=PIPE)

        stdout, stderr = proc.communicate()
        return_code = proc.returncode

        tmp = []

        # remove trailing whitespace before splitting each line into pairs.
        for line in stdout.strip().split('\n'):
            qiita_id, file_path = line.split('\t')
            # truncate full-path output to be file-system agnostic.
            file_path = re.sub('^.*metagenomics_pooling_notebook/',
                               'metagenomics_pooling_notebook/', file_path)
            tmp.append(f'{qiita_id}\t{file_path}')

        stdout = '\n'.join(tmp)

        self.assertEqual(('1111\tmetagenomics_pooling_notebook/metapool/tests'
                          '/VFTEST/200318_A00953_0082_AH5TWYDSXY.Project_1111'
                          '.1.tsv\n1111\tmetagenomics_pooling_notebook/metapo'
                          'ol/tests/VFTEST/200318_A00953_0082_AH5TWYDSXY.Proj'
                          'ect_1111.3.tsv\n666\tmetagenomics_pooling_notebook'
                          '/metapool/tests/VFTEST/200318_A00953_0082_AH5TWYDS'
                          'XY.Trojecp_666.3.tsv'), stdout)
        self.assertEqual('', stderr)
        self.assertEqual(0, return_code)


class SeqproBCLConvertTests(unittest.TestCase):
    def setUp(self):
        # we need to get the test data directory in the parent directory
        # important to use abspath because we use CliRunner.isolated_filesystem
        tests_dir = os.path.abspath(os.path.dirname(__file__))
        tests_dir = os.path.dirname(os.path.dirname(tests_dir))
        self.data_dir = os.path.join(tests_dir, 'tests', 'data')

        self.fastp_run = os.path.join(self.data_dir, 'runs',
                                      '200318_A00953_0082_AH5TWYDSXY')
        self.fastp_sheet = os.path.join(self.fastp_run, 'sample-sheet.csv')

        # before continuing, create a copy of 200318_A00953_0082_AH5TWYDSXY
        # and replace Stats sub-dir with Reports.
        self.temp_copy = self.fastp_run.replace('200318', '200418')
        copytree(self.fastp_run, self.temp_copy)
        rmtree(join(self.temp_copy, 'Stats'))
        os.makedirs(join(self.temp_copy, 'Reports'))
        copy(join(self.data_dir, 'Demultiplex_Stats.csv'),
             join(self.temp_copy, 'Reports', 'Demultiplex_Stats.csv'))

    def test_fastp_run(self):
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(format_preparation_files,
                                   args=[self.temp_copy, self.fastp_sheet,
                                         './', '--pipeline',
                                         'fastp-and-minimap2'])
            self.assertEqual(result.output, '')
            self.assertEqual(result.exit_code, 0)

            exp_preps = [
                '200418_A00953_0082_AH5TWYDSXY.Project_1111.1.tsv',
                '200418_A00953_0082_AH5TWYDSXY.Project_1111.3.tsv',
                '200418_A00953_0082_AH5TWYDSXY.Trojecp_666.3.tsv'
            ]

            self.assertEqual(sorted(os.listdir('./')), exp_preps)

            for prep, exp_lines in zip(exp_preps, [4, 4, 5]):
                with open(prep) as f:
                    self.assertEqual(len(f.read().split('\n')), exp_lines,
                                     'Assertion error in %s' % prep)

    def tearDown(self):
        rmtree(self.temp_copy)


if __name__ == '__main__':
    unittest.main()
