import os
import unittest
from ipykernel.zmqshell import ZMQInteractiveShell

from elastic.test.test_utils import get_problem_setting
from elastic.core.notebook.checkpoint import checkpoint
from elastic.algorithm.baseline import MigrateAllBaseline
from elastic.core.io.recover import resume

TEST_FILE_PATH = "./tmp_test_file"


class TestCheckpoint(unittest.TestCase):

    def test_checkpoint(self):
        """
            Test checkpointing correctly identifies active variables.
        """
        # Checkpoint the example graph by migrating all variables.
        shell = ZMQInteractiveShell()
        shell.user_ns["x"] = 1
        shell.user_ns["y"] = 2
        graph, _ = get_problem_setting()
        checkpoint(graph, shell, MigrateAllBaseline(migration_speed_bps=1), TEST_FILE_PATH)
        self.assertTrue(os.path.exists(TEST_FILE_PATH))

        # Recover the checkpoint.
        graph2, variables, vss_to_migrate2, vss_to_recompute2, oes_to_recompute2 = resume(TEST_FILE_PATH)

        # Variables 'x' and 'y' should be successfully migrated.
        self.assertEqual("x", variables[graph2.cell_executions[1]][0][0].name)
        self.assertEqual(1, variables[graph2.cell_executions[1]][0][1])
        self.assertEqual("y", variables[graph2.cell_executions[2]][0][0].name)
        self.assertEqual(2, variables[graph2.cell_executions[2]][0][1])

        # Variable 'z' should not have been migrated as it has been marked as deleted.
        self.assertEqual(0, len(variables[graph2.cell_executions[0]]))


if __name__ == '__main__':
    unittest.main()
