class Sorter:
    def __init__(self, meta_info):
        self.meta_info = meta_info


    ###############################################################################################
    # Main
    ###############################################################################################
    def run(self):
        print(f"Start sorting")

        print(f"Finished sorting")

        self.meta_info.finished = True
