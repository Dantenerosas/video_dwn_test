from multiprocessing import freeze_support

from src.core.master_service import MasterService

if __name__ == '__main__':
    freeze_support()
    ms = MasterService()
    ms.loop.run_until_complete(ms.run())