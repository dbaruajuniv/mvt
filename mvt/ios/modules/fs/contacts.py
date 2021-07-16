# Mobile Verification Toolkit (MVT)
# Copyright (c) 2021 MVT Project Developers.
# See the file 'LICENSE' for usage and copying permissions, or find a copy at
#   https://github.com/mvt-project/mvt/blob/main/LICENSE

import sqlite3

from .base import IOSExtraction

CONTACTS_BACKUP_IDS = [
    "31bb7ba8914766d4ba40d6dfb6113c8b614be442",
]
CONTACTS_ROOT_PATHS = [
    "private/var/mobile/Library/AddressBook/AddressBook.sqlitedb",
]

class Contacts(IOSExtraction):
    """This module extracts all contact details from the phone's address book."""

    def __init__(self, file_path=None, base_folder=None, output_folder=None,
                 fast_mode=False, log=None, results=[]):
        super().__init__(file_path=file_path, base_folder=base_folder,
                         output_folder=output_folder, fast_mode=fast_mode,
                         log=log, results=results)

    def run(self):
        self._find_ios_database(backup_ids=CONTACTS_BACKUP_IDS, root_paths=CONTACTS_ROOT_PATHS)
        self.log.info("Found Contacts database at path: %s", self.file_path)

        conn = sqlite3.connect(self.file_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT
                multi.value, person.first, person.middle, person.last,
                person.organization
            FROM ABPerson person, ABMultiValue multi
            WHERE person.rowid = multi.record_id and multi.value not null
            ORDER by person.rowid ASC;
        """)
        names = [description[0] for description in cur.description]

        for entry in cur:
            new_contact = dict()
            for index, value in enumerate(entry):
                new_contact[names[index]] = value

            self.results.append(new_contact)

        cur.close()
        conn.close()

        self.log.info("Extracted a total of %d contacts from the address book", len(self.results))