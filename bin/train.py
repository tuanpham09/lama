#!/usr/bin/env python3

import logging
import os
import sys
import traceback

os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

import hydra
from omegaconf import OmegaConf
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.plugins import DDPPlugin

from saicinpainting.training.trainers import make_training_model
from saicinpainting.utils import register_debug_signal_handlers, handle_ddp_subprocess, handle_ddp_parent_process, \
    handle_deterministic_config

LOGGER = logging.getLogger(__name__)


@handle_ddp_subprocess()
@hydra.main(config_path='../configs/training', config_name='tiny_test.yaml')
def main(config: OmegaConf):
    try:
        need_set_deterministic = handle_deterministic_config(config)

        if sys.platform != 'win32':
            register_debug_signal_handlers()  # kill -10 <pid> will result in traceback dumped into log

        is_in_ddp_subprocess = handle_ddp_parent_process()

        config.visualizer.outdir = os.path.join(os.getcwd(), config.visualizer.outdir)
        if not is_in_ddp_subprocess:
            LOGGER.info(OmegaConf.to_yaml(config))
            OmegaConf.save(config, os.path.join(os.getcwd(), 'config.yaml'))

        checkpoints_dir = os.path.join(os.getcwd(), 'models')
        os.makedirs(checkpoints_dir, exist_ok=True)

        # there is no need to suppress this logger in ddp, because it handles rank on its own
        metrics_logger = TensorBoardLogger(config.location.tb_dir, name=os.path.basename(os.getcwd()))
        metrics_logger.log_hyperparams(config)

        training_model = make_training_model(config)

        trainer_kwargs = OmegaConf.to_container(config.trainer.kwargs, resolve=True)
        if need_set_deterministic:
            trainer_kwargs['deterministic'] = True

        trainer = Trainer(
            # there is no need to suppress checkpointing in ddp, because it handles rank on its own
            callbacks=ModelCheckpoint(dirpath=checkpoints_dir, **config.trainer.checkpoint_kwargs),
            logger=metrics_logger,
            default_root_dir=os.getcwd(),
            **trainer_kwargs
        )
        trainer.fit(training_model)
    except KeyboardInterrupt:
        LOGGER.warning('Interrupted by user')
    except Exception as ex:
        LOGGER.critical(f'Training failed due to {ex}:\n{traceback.format_exc()}')
        sys.exit(1)


if __name__ == '__main__':
    main()
else:
    # Khi được import như một module
    # Cấu hình đường dẫn cho hydra khi chạy như một package đã cài đặt
    import os
    import sys
    from pathlib import Path
    
    # Xác định đường dẫn cấu hình tương đối so với vị trí của module này
    module_path = Path(__file__).parent.parent
    config_path = os.path.join(module_path, 'configs', 'training')
    
    # Cập nhật decorator hydra.main với đường dẫn mới
    main = hydra.main(config_path=config_path, config_name='tiny_test.yaml')(main)
