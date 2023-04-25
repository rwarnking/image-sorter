# https://realpython.com/python-application-layouts/
# https://realpython.com/python-modules-packages/
# https://github.com/navdeep-G/samplemod
# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
import pathmagic  # noqa isort:skip

import os
import shutil
import re
import unittest
from os.path import isfile, join
from tkinter import Text, Tk

from database import Database
from meta_information import MetaInformation
from sorter import Sorter
from sort_file_states import file_rules
from testfile_creator import create_all_test_files

import piexif


IMAGE_FOLDER = "test_images"

class TestSort(unittest.TestCase):
    def test_run(self):
        TEST_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_DIR = join(TEST_DIR, "test_dbs")
        IMAGE_DIR = join(TEST_DIR, IMAGE_FOLDER)
        RESULT_DIR = join(TEST_DIR, "result_images")

        window = Tk()

        # Set the meta_info data
        meta_info = MetaInformation()
        meta_info.set_dirs(IMAGE_DIR, RESULT_DIR, DB_DIR, DB_DIR)

        # load database
        self.db = Database()
        self.db.load_from_file(join(DB_DIR, "db_test_4-1.json"))

        # Creating testfiles if not present
        # OBACHT: This does not check if the folder contains files
        if not os.path.exists(IMAGE_DIR):
            os.mkdir(IMAGE_DIR)
            create_all_test_files(IMAGE_FOLDER)

        # Check that the path to which the files will be copied exists
        if os.path.exists(RESULT_DIR):
            shutil.rmtree(RESULT_DIR)
        os.mkdir(RESULT_DIR)

        #############
        # Copy test #
        #############
        # Get a list of setting combinations and iterate it.
        # The list should contain most of the combinations that are possible.
        for settings in self.get_settings_list(meta_info):
            meta_info.finished = False
            self.set_meta_info(meta_info, settings)

            # Run the sort process
            s = Sorter(meta_info)
            s.run()

            # while not meta_info.text_queue.empty():
            #     print(meta_info.text_queue.get(0))

            # Run all checks for the current settings
            self.run_checks(meta_info, settings, IMAGE_DIR)

            # Clear result folder
            shutil.rmtree(RESULT_DIR)
            os.mkdir(RESULT_DIR)

        #############
        # Move test #
        #############
        meta_info.finished = False
        settings = self.create_settings_obj(meta_info)
        settings["copy_files"] = 0
        self.set_meta_info(meta_info, settings)

        # Run the sort process
        s = Sorter(meta_info)
        s.run()

        files_list = [1 for _, _, files in os.walk(IMAGE_DIR) if len(files) > 0]
        self.assertTrue(len(files_list) == 0, "Moving files did not succeed!")

        # Clear result folder
        shutil.rmtree(IMAGE_DIR)
        shutil.rmtree(RESULT_DIR)
        os.mkdir(RESULT_DIR)
        
    def get_settings_list(self, meta_info):
        """
        Creates a list of setting objects that should be tested.
        The tool allows to customize multiple things:
        - used input from the file for dataextraction
        - file output signature
        - folder output signature
        - multiple processing options (recursive, require_artist, ...)
        For each of these customizations a settings object is generated.
        This means that a lot of these are similar to each other,
        often only different in one setting.
        @return The list with all generated setting objects
        """
        # The final list
        settings = []

        # List of options, that can either enabled or disabled
        lst_options = [
            "recursive",
            "process_unmatched",
            "require_artist",
            "process_samename",
        ]
        # Calculate the maximum number of combinations
        # uses binary increament -> 000, 001, 010, 011, 100, ...
        option_max = pow(2, len(lst_options))
        excluded = 0

        # Generate all tests for each of the supported output file signatures
        # Folder are tested implicitly, since the files require matching folder
        for out_choice in meta_info.get_supported_file_signatures():
            # Generate all tests for each of the supported input types
            for read_choice in meta_info.get_read_choices():
                option_int = 0
                # Create a test for each option combination
                for _ in range(option_max):
                    # Get object with default settings
                    obj = self.create_settings_obj(meta_info)

                    # Iterate the option-list and assign their values
                    tmp = option_int
                    for idx in range(len(lst_options)):
                        obj[lst_options[idx]] = tmp % 2
                        tmp //= 10

                    # Discard invalid setting combinations
                    if out_choice == "Foldername_Number" and obj["process_samename"]:
                        excluded += 1
                        continue

                    # Assign the current setting for in and output
                    obj["in_signature"] = read_choice
                    obj["file_signature"] = out_choice
                    settings.append(obj)

                    # Increment option combination
                    if option_int % 2 == 1:
                        option_int *= 10
                    else:
                        option_int += 1

        # Test that as much setting objects were generated as expected
        self.assertTrue(
            len(settings) + excluded == len(meta_info.get_read_choices()) *
            len(meta_info.get_supported_file_signatures()) * option_max,
            f"Setting length mismatch: {len(settings)}"
        )

        # Add aditional settings case for metadata
        obj = self.create_settings_obj(meta_info)
        obj["metadata"] = 1
        obj["recursive"] = 0
        obj["process_unmatched"] = 0
        settings.append(obj)

        return settings

    def run_checks(self, meta_info, settings, IMAGE_DIR):
        """
        Run all checks for the current settings.
        For this the information from sort_file_status.py
        is parsed. The file contains a dictionary list in which
        for each file the correct combination of folder and file name for all possible
        setting combinations is saved. 
        This allows to parse the information and use it to test against. 
        """
        BASE_DIR = meta_info.img_tgt.get()

        # Number of processed files to check against the number of files in the final folder.
        case_count = 0
        # Dictionary to save the number of files in each subfolder.
        # This is only used when the file_signature is Foldername_Number.
        file_counts = {}

        # Number of files that should be in the folder
        tests_count = 0

        # Debugging info
        print("############################################")
        print(f"Input signature: {settings['in_signature']}")
        print(f"Output signature: {settings['file_signature']}")
        print(f"Folder signature: {settings['folder_signature']}")
        print(f"Process unmatched: {settings['process_unmatched']}")
        print(f"Require artist: {settings['require_artist']}")
        print(f"Process same name: {settings['process_samename']}")
        print(f"Modify metadata: {settings['modify_meta']}")
        print(f"Recursive: {settings['recursive']}")
        print("############################################")

        # Get a list of all files that will be processed
        lst_files = []
        if meta_info.recursive.get() == 1:
            for cur_path, d, files in os.walk(IMAGE_DIR):
                lst_tmp = []
                for f in files:
                    if isfile(join(cur_path, f)):
                        # Check for a recursive folder, add to name if present
                        res_split = cur_path.split(join(IMAGE_FOLDER, ""))
                        if len(res_split) == 2:
                            lst_tmp.append(join(res_split[-1], f))
                        else:
                            lst_tmp.append(f)
                lst_tmp.sort(key=lambda f: os.path.splitext(f)[1].lower() != ".jpg")  
                lst_files.extend(lst_tmp)
        else:
            lst_files = [f for f in os.listdir(IMAGE_DIR) if isfile(join(IMAGE_DIR, f))]
            lst_files.sort(key=lambda f: os.path.splitext(f)[1].lower() != ".jpg")  

        self.assertTrue(len(lst_files) > 40, f"File list does contain to few elements: {len(lst_files)}!")

        for file in lst_files:
            f_name, f_ext = os.path.splitext(file)

            self.assertTrue(f_name in file_rules, f"Found missing rule for {f_name}!")
            file_rule = file_rules[f_name]

            ##################
            # Get valid case #
            ##################
            found_case = False
            # Iterate all possible cases that are defined for this file
            for case in file_rule["cases"]:

                # Use the first found case
                if found_case:
                    continue
                # Test if the conditions of the current case are met
                found_case = True
                for condition in case["conditions"]:
                    found_case &= settings[condition[0]] == condition[1]
                # Check if rule is valid for this case
                if f_ext == ".jpg":
                    found_case &= case["jpg"]
                # If the case is valid use its folder information
                if found_case:
                    case_count += 1

                    # Get folder
                    if current_folder:= case["folder"]:
                        # Get filename
                        expected_name = file_rule["out"][case["name"]][settings["file_signature"]]

                        # Special case for the file_signature Foldername_Number!
                        # Since this case uses the number of files in the target folder, 
                        # the filecounts for each folder must be saved.
                        # Furthermore the file name is also dependent on the folder it is in.
                        if settings["file_signature"] == "Foldername_Number" and current_folder != "misc":
                            if current_folder not in file_counts:
                                file_counts[current_folder] = 1
                            else:
                                file_counts[current_folder] += 1

                            folder_name = re.sub(r"[/\\]no_artist", "", current_folder)
                            folder_name = re.split(r"[/\\]", folder_name)[-1]
                            expected_name = f"{folder_name}_{file_counts[current_folder]:03d}"

                        cmpl_dir = join(BASE_DIR, current_folder)
                        file_dir = join(cmpl_dir, f"{expected_name}{f_ext}")
                        self.assertTrue(os.path.exists(file_dir), f"Missing file: {file_dir}!")

                        # Metadata check
                        # OBACHT: Currently only the title is checked, since the file_rules
                        # do not provide more information
                        if f_ext == ".jpg" and "meta" in file_rule:
                            self.check_meta(file_dir, file_rule["meta"], settings["modify_meta"])

                        tests_count += 1

            self.assertTrue(found_case, "Was not able to find case for settings!")
            
        self.assertTrue(case_count == len(lst_files), f"File counts do not match: {case_count} : {len(lst_files)}!")
        dir_info = [(len(files), cur_path) for cur_path, _, files in os.walk(BASE_DIR)]
        tgt_counts, _ = zip(*dir_info)
        tgt_counts = sum(tgt_counts)
        self.assertTrue(tests_count == tgt_counts, f"File counts do not match (tgt dir): {tests_count} : {tgt_counts}!")

        # Check if all files are still present in IMG source.
        for file in lst_files:
            self.assertTrue(os.path.exists(join(meta_info.img_src.get(), file)), f"Found missing file {file}!")

    def check_meta(self, file_with_path, metadata, state):
        try:
            exif_dict = piexif.load(file_with_path)
        except FileNotFoundError:
            return

        for elem in metadata:
            value = self.get_exif_value(exif_dict, elem["dict"], elem["key"])

            self.assertTrue(
                elem["value_enabled" if state == 1 else "value_disabled"] == value,
                f"Metainfo-value mismatch! ({value}, {elem['value_enabled' if state else 'value_disabled']})"
            )

    def get_exif_value(self, exif_dict, dict1, key):
        if (
            key in exif_dict[dict1]
            and len((exif_dict[dict1][key]).decode("ascii")) > 0
        ):
            return str(exif_dict[dict1][key], "ascii")
        else:
            return None

    def set_meta_info(self, meta_info, settings):
        """
        Helper function for transfer the values from the settings object to the meta_info object. 
        """
        meta_info.modify_meta.set(settings["modify_meta"])
        meta_info.overwrite_meta.set(settings["overwrite_meta"])
        meta_info.recursive.set(settings["recursive"])
        meta_info.copy_files.set(settings["copy_files"])
        meta_info.process_unmatched.set(settings["process_unmatched"])
        meta_info.require_artist.set(settings["require_artist"])
        meta_info.process_samename.set(settings["process_samename"])
        meta_info.dont_ask_again.set(settings["dont_ask_again"])

        meta_info.in_signature.set(settings["in_signature"])
        meta_info.file_signature.set(settings["file_signature"])
        meta_info.folder_signature.set(settings["folder_signature"])

    def create_settings_obj(self, meta_info):
        """
        Helper function for generating a default settings object.
        """
        obj = {
            "modify_meta": 1,
            "overwrite_meta": 1,
            "recursive": 1,
            "copy_files": 1,
            "process_unmatched": 1,
            "require_artist": 1,
            "process_samename": 0,
            "dont_ask_again": False,
            "in_signature": meta_info.get_read_choices()[0],
            "file_signature": meta_info.get_supported_file_signatures()[0],
            "folder_signature": meta_info.get_supported_folder_signatures()[0],
        }
        return obj
