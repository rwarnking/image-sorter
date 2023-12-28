TooltipDict = {
    # Main application: first section
    "btn_src": "Browse for a folder in which to find the images to process.",
    "btn_tgt": "Browse for a folder to save the sorted images in.",
    # Main application: second section
    "rbtn_Metadata, fallback: Filename": "Prefer metadata for file information,\
        \nif metadata is not parseable use the filename.",
    "rbtn_Filename, fallback: Metadata": "Prefer filename for file information,\
        \nif filename is not parseable use the metadata.",
    "rbtn_Metadata only": "Use only metadata for file information.",
    "rbtn_Filename only": "Use only filename for file information.",
    "cb_filesig_select": "Select output signature for the new filename.",
    "cb_foldersig_select": "Select output signature of the folderstructure.",
    # Main application: third section
    "btn_mod_db": "Modify the database, including events and artists.",
    # Main application: forth section
    "cb_recursive": "Enable or disable recursive folder processing.\
        \nIf enabled subfolder are also processed.",
    "cb_unmatched": "Enable or disable copying of unmatched files.\
        \nIf enabled files that could not be processed are copied to a misc folder.\
        \nOtherwise they are ignored.",
    "cb_samename": "Enable or disable processing of files with identical name.\
        \nIf enabled identical named files are renamed according to the first processed file.",
    "cb_reqartist": "Enable or disable requirement of an artist.\
        \nIf enabled files without artist are copied to a folder called no_artist.\
        \nDoes apply to non .jpg-files.",
    "cb_modmeta": "Enable or disable metadata modification.\
        \nIf enabled information like title & artist are added to the metadata.",
    "cb_overmeta": "Enable or disable overwriting metadata.\
        \nIf enabled metadata information is overwriten in case it is already present.",
    "rbtn_copyfile": "If selected the images are copied.",
    "rbtn_movefile": "If selected the images are moved.",
    # Main application: last section
    "btn_run": "Start the sorting process, all files will be processed \
        \naccording to the selected rules and using the current database.",
    # Database modification window
    "btn_loadfile": "Browse for a json file to load the database from.\
        \nEverthing is loaded directly after file selection.",
    "btn_savefile": "Browse for a json file to save the database to.\
        \nEverthing is loaded directly after file selection.",
    "btn_reorder": "Reorder all tables of the currently loaded database by date.",
    "cb_dbs": "Select a table from the database to inspect and modify.",
    "btn_add": "Add one element to the selected table.",
    "btn_del": "Delete the element in this row.",
    "btn_mod": "Modify the element in this row.",
    "btn_clear": "Clears the selected table by deleting all its entrys.",
    "btn_clear_month": "Deletes all entrys of the current month for the selected table.",
    "btn_done": "Close this window and return to the previous one.",
    # Add/Mod event window
    "ent_e_title": "Enter the title of the event.",
    "btn_add_part": "Add a participant to the event.",
    "btn_del_part": "Delete this participant from the event.",
    "btn_add_sube": "Add a subevent to the event.",
    "btn_del_sube": "Delete this subevent from the event.",
    "btn_add_event": "Add or update this event to the event table and the database.",
    # Add/Mod participant window
    "cb_part_person": "Enter or select the person that is the participant.",
    # Add/Mod subevent window
    "ent_se_title": "Enter the title of the subevent.",
    # Add/Mod artist window
    "cb_a_person": "Enter or select the person that is the artist.",
    "ent_a_make": "Set the camera make of the artist.",
    "ent_a_model": "Set the camera model of the artist.",
    "sp_a_shift": "Enter a time correction for the time stamp of all images of this artist.",
    "btn_add_art": "Add this artist to the database.",
    "btn_update_art": "Update this artists data.",
    # Add/Mod person window
    "ent_p_name": "Enter or modify the name of the person.",
    "btn_add_psn": "Add this person to the database.",
    "btn_update_psn": "Update this persons name.",
    # Misc
    "btn_abort": "Close this window and return to the previous one \
        \nwithout applying any changes.",
    "date_start": "Select the start day.",
    "date_end": "Select the end day.",
    "hs_start": "Select the start hour.",
    "ms_start": "Select the start minute.",
    "hs_end": "Select the end hour.",
    "ms_end": "Select the end minute.",
}
