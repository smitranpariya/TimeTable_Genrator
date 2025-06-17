from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton,QMessageBox
from PyQt6.QtCore import pyqtSignal
import pymongo,random
import traceback


class TimetableDialog(QDialog):
    timetable_generated = pyqtSignal()  # Signal to indicate timetable generation
    print("initializing dailogbox")
    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            print("initializing init")
            self.setWindowTitle("Select Year and Semester")

            layout = QVBoxLayout()

            # Year Selection
            self.year_label = QLabel("Select Year:")
            self.year_combo = QComboBox()
            self.year_combo.addItems(["1st Year", "2nd Year", "3rd Year", "4th Year"])
            layout.addWidget(self.year_label)
            layout.addWidget(self.year_combo)

            # Semester Selection
            self.sem_label = QLabel("Select Semester:")
            self.sem_combo = QComboBox()
            layout.addWidget(self.sem_label)
            layout.addWidget(self.sem_combo)

            # Specialization Selection
            self.spec_label = QLabel("Select Specialization:")
            self.spec_combo = QComboBox()
            self.spec_combo.addItems(["AI", "CS", "DS", "Cloud Computing"])
            self.spec_label.hide()
            self.spec_combo.hide()
            layout.addWidget(self.spec_label)
            layout.addWidget(self.spec_combo)

            # Generate Button
            self.generate_button = QPushButton("Generate Timetable")
            self.generate_button.clicked.connect(self.generate_timetable)
            layout.addWidget(self.generate_button)

            self.setLayout(layout)

            # Now connect the signal
            self.year_combo.currentIndexChanged.connect(self.update_semesters)

            # Now call update_semesters safely — after all widgets exist
            self.update_semesters(0)
        except Exception as e:
            print(e)


    def update_semesters(self, index):
        """Update semester options and show specialization if needed."""
        year_semesters = {
            0: ["1st Semester", "2nd Semester"],  # 1st Year
            1: ["3rd Semester", "4th Semester"],  # 2nd Year
            2: ["5th Semester", "6th Semester"],  # 3rd Year
            3: ["7th Semester", "8th Semester"]   # 4th Year
        }

        self.sem_combo.clear()
        self.sem_combo.addItems(year_semesters.get(index, []))

        # Show specialization for 3rd (index 2) and 4th (index 3) year
        if index in (2, 3):
            self.spec_label.show()
            self.spec_combo.show()
        else:
            self.spec_label.hide()
            self.spec_combo.hide()


    def get_selected_year_sem(self):
        """Return selected year, semester, and specialization (if applicable)"""
        year_mapping = {
            "1st Year": 1,
            "2nd Year": 2,
            "3rd Year": 3,
            "4th Year": 4
        }

        sem_mapping = {
            "1st Semester": 1,
            "2nd Semester": 2,
            "3rd Semester": 3,
            "4th Semester": 4,
            "5th Semester": 5,
            "6th Semester": 6,
            "7th Semester": 7,
            "8th Semester": 8
        }

        selected_year = year_mapping[self.year_combo.currentText()]
        selected_sem = sem_mapping[self.sem_combo.currentText()]

        # Check if specialization is visible, if so return it, else None
        selected_spec = self.spec_combo.currentText() if self.spec_combo.isVisible() else None

        return selected_year, selected_sem , selected_spec
    
    def generate_timetable(self):
        """Trigger timetable generation when button is clicked"""
        year, semester, selected_spec = self.get_selected_year_sem()  # Get year & semester as integers

        try:
            generator = TimetableGenerator(year, semester , selected_spec)
            timetable = generator.generate_timetable()  # Store generated timetable

            if timetable:
                QMessageBox.information(
                    self, "Success", 
                    f"Timetable for Year {year}, Semester {semester} generated successfully!"
                )
                self.timetable_generated.emit()  # Emit signal
            else:
                QMessageBox.warning(
                    self, "No Data", 
                    "No subjects or faculty data found for the selected year and semester."
                )
        except Exception as e:
            print(f"{e}")
            QMessageBox.critical(
                self, "Error", f"An error occurred while generating the timetable:\n{str(e)}"
            )


class TimetableGenerator:

    def __init__(self, year, semester, specialization=None):
        self.year = year
        self.semester = semester
        self.specialization = specialization
        print(f"Generator initialized with Year: {year}, Semester: {semester}, Specialization: {specialization}")
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["timetable_db"]
        self.timetable = {}

    def fetch_data(self):
        """Fetch all required data from the database with proper formatting and error handling."""
        try:
            self.rooms = list(self.db["rooms"].find())
            self.labs = list(self.db["labs"].find())

            # Map year to match DB format
            year_map = {
                "1": "1st Year",
                "2": "2nd Year",
                "3": "3rd Year",
                "4": "4th Year"
            }
            year_str = year_map.get(str(self.year), f"{self.year} Year")

            # Convert semester value to DB format if needed
            semester_str = f"Semester {self.semester}"  # Match "Semester 1" style

            # Build query
            query = {"year": year_str, "semester": semester_str}
            if self.specialization and self.specialization != "None":  # Only add if specialization is provided and not "None"
                query["specialization"] = self.specialization

            print(f"Fetching subjects with query: {query}")

            self.subjects = list(self.db["Subject_collection"].find(query))

            # Debug: Print fetched subjects to verify
            print(f"Fetched subjects: {[sub for sub in self.subjects]}")

            if not self.subjects:
                raise ValueError(f"No subjects found for {year_str} - {semester_str} with specialization {self.specialization or 'None'}.")

            if not self.rooms:
                raise ValueError("No rooms found in the database.")

        except Exception as e:
            print(f"Error fetching data: {e}")
            return False

        return True

    def delete_timetable(db, year, semester, batch, specialization):
        """Delete a timetable and update room, lab, and faculty/TA occupancy."""
        try:
            # Step 1: Fetch all timetables to debug the structure
            all_timetables = list(db["timetable"].find())
            print("All timetables in database:", all_timetables)

            # Step 2: Construct the query with correct types
            timetable_query = {
                "year": year,  # Integer, e.g., 3
                "semester": semester,  # Integer, e.g., 5
                "batch": batch,  # Integer, e.g., 1
                "specialization": specialization if specialization != "None" else "None"  # String, e.g., "AI"
            }
            print(f"Fetching timetable with query: {timetable_query}")
            timetable_data = db["timetable"].find_one(timetable_query)

            if not timetable_data:
                print(f"No timetable found for {timetable_query}")
                return False

            # Step 3: Update room and lab occupancy
            room_lab_occupancy_collection = db["room_lab_occupancy"]
            room_lab_occupancy = room_lab_occupancy_collection.find_one() or {
                day: {slot: {"rooms": [], "labs": []} for slot in [
                    "9:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30",
                    "1:30 - 2:30", "2:30 - 3:30", "3:30 - 4:30", "4:30 - 5:30"
                ]} for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            }

            for day, slots in timetable_data.get("data", {}).items():
                for slot, session in slots.items():
                    if session and session["type"] in ["Theory", "Tutorial"]:
                        room = session.get("room")
                        if room and day in room_lab_occupancy and slot in room_lab_occupancy[day]:
                            if room in room_lab_occupancy[day][slot]["rooms"]:
                                room_lab_occupancy[day][slot]["rooms"].remove(room)
                    elif session and session["type"] == "Lab":
                        lab = session.get("lab")
                        if lab and day in room_lab_occupancy and slot in room_lab_occupancy[day]:
                            if lab in room_lab_occupancy[day][slot]["labs"]:
                                room_lab_occupancy[day][slot]["labs"].remove(lab)

            room_lab_occupancy_collection.update_one(
                {}, {"$set": room_lab_occupancy}, upsert=True
            )
            print(f"Updated room_lab_occupancy for deleted timetable: {timetable_query}")

            # Step 4: Update faculty and TA occupancy
            faculty_ta_occupancy_collection = db["faculty_ta_occupancy"]
            faculty_ta_occupancy = faculty_ta_occupancy_collection.find_one() or {
                day: {slot: [] for slot in [
                    "9:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30",
                    "1:30 - 2:30", "2:30 - 3:30", "3:30 - 4:30", "4:30 - 5:30"
                ]} for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            }

            for day, slots in timetable_data.get("data", {}).items():
                for slot, session in slots.items():
                    if session and "instructor" in session:
                        instructor = session["instructor"]
                        if day in faculty_ta_occupancy and slot in faculty_ta_occupancy[day]:
                            if instructor in faculty_ta_occupancy[day][slot]:
                                faculty_ta_occupancy[day][slot].remove(instructor)

            faculty_ta_occupancy_collection.update_one(
                {}, {"$set": faculty_ta_occupancy}, upsert=True
            )
            print(f"Updated faculty_ta_occupancy for deleted timetable: {timetable_query}")

            # Step 5: Delete the timetable entry
            db["timetable"].delete_one(timetable_query)
            print(f"Timetable deleted for {timetable_query}")
            return True

        except Exception as e:
            print(f"Error deleting timetable: {e}")
            return False

    def generate_timetable(self):
        """Generate and save the timetable ensuring no faculty/TA conflicts across batches, years, or specializations."""
        if not self.fetch_data():
            print("Failed to generate timetable due to missing data.")
            return None

        # Fetch strength details for the given year and specialization
        strength_query = {"year": str(self.year)}
        if self.year in [3, 4] and self.specialization and self.specialization != "None":
            strength_query["specialization"] = self.specialization
        else:
            strength_query["specialization"] = None

        print(f"Fetching strength details with query: {strength_query}")
        strength_info = self.db["strength_details"].find_one(strength_query)

        if not strength_info:
            print(f"No section details found for year {self.year}, specialization {self.specialization or 'None'}.")
            return None

        print(f"Strength info fetched: {strength_info}")

        num_batches = int(strength_info["sections"])
        total_students = int(strength_info["students"])
        batch_strength = round(total_students / num_batches)

        time_slots = [
            "9:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30",
            "1:30 - 2:30", "2:30 - 3:30", "3:30 - 4:30", "4:30 - 5:30"
        ]

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        # Identify faculty and TAs teaching multiple subjects or across specializations/years
        all_subjects = list(self.db["Subject_collection"].find())
        faculty_ta_counts = {}

        for subject in all_subjects:
            year = subject["year"]
            specialization = subject.get("specialization", "None")
            subject_name = subject["subject"]
            subject_type = subject["type"]
            instructor = subject.get("faculty", subject.get("ta", "N/A"))

            if instructor == "N/A":
                continue

            key = (instructor, subject_type)
            if key not in faculty_ta_counts:
                faculty_ta_counts[key] = []
            faculty_ta_counts[key].append({
                "subject": subject_name,
                "year": year,
                "specialization": specialization
            })

        faculty_ta_to_track = {}
        for (instructor, subject_type), assignments in faculty_ta_counts.items():
            subjects = set(assignment["subject"] for assignment in assignments)
            year_spec_pairs = set((assignment["year"], assignment["specialization"]) for assignment in assignments)

            if len(subjects) > 1 or len(year_spec_pairs) > 1:
                faculty_ta_to_track[instructor] = subject_type

        print(f"Faculty/TA to track for conflicts: {faculty_ta_to_track}")

        # Initialize or update the faculty_ta_occupancy collection
        faculty_ta_occupancy_collection = self.db["faculty_ta_occupancy"]
        faculty_ta_occupancy = {day: {slot: set() for slot in time_slots} for day in days}

        existing_occupancy = faculty_ta_occupancy_collection.find_one()
        if existing_occupancy:
            for day in days:
                for slot in time_slots:
                    faculty_ta_occupancy[day][slot] = set(existing_occupancy.get(day, {}).get(slot, []))

        timetables = []

        if self.year in [3, 4] and self.specialization and self.specialization != "None":
            spec = self.specialization

            for batch in range(1, num_batches + 1):
                weekly_schedule = {day: {slot: None for slot in time_slots} for day in days}

                lab_subjects = [sub for sub in self.subjects if sub["type"] == "Lab"]
                assigned_labs = set()

                for lab in lab_subjects:
                    assigned = False
                    attempts = 0
                    ta = lab.get("ta", "N/A")
                    while not assigned and attempts < 100:
                        day = random.choice(days)
                        slot_index = random.randint(0, len(time_slots) - 2)

                        ta_conflict = (
                            ta in faculty_ta_to_track and
                            (ta in faculty_ta_occupancy[day][time_slots[slot_index]] or
                            ta in faculty_ta_occupancy[day][time_slots[slot_index + 1]])
                        )

                        if (slot_index != 2 and
                            not weekly_schedule[day][time_slots[slot_index]] and 
                            not weekly_schedule[day][time_slots[slot_index + 1]] and
                            not ta_conflict and
                            lab["subject"] not in assigned_labs and
                            not any(s and s.get("type") == "Lab" for s in weekly_schedule[day].values())):
                            
                            weekly_schedule[day][time_slots[slot_index]] = {
                                "subject": lab["subject"],
                                "type": "Lab",
                                "instructor": ta
                            }
                            weekly_schedule[day][time_slots[slot_index + 1]] = {
                                "subject": lab["subject"],
                                "type": "Lab",
                                "instructor": ta
                            }
                            
                            if ta in faculty_ta_to_track:
                                faculty_ta_occupancy[day][time_slots[slot_index]].add(ta)
                                faculty_ta_occupancy[day][time_slots[slot_index + 1]].add(ta)
                            
                            assigned_labs.add(lab["subject"])
                            assigned = True
                        attempts += 1

                    if not assigned:
                        print(f"Warning: Could not assign lab {lab['subject']} for batch {batch}, specialization {spec}.")

                tutorial_subjects = [sub for sub in self.subjects if sub["type"] == "Tutorial"]

                for tutorial in tutorial_subjects:
                    assigned = False
                    attempts = 0
                    ta = tutorial.get("ta", "N/A")
                    while not assigned and attempts < 100:
                        day = random.choice(days)
                        slot = random.choice(time_slots)

                        ta_conflict = (
                            ta in faculty_ta_to_track and
                            ta in faculty_ta_occupancy[day][slot]
                        )

                        if not weekly_schedule[day][slot] and not ta_conflict:
                            weekly_schedule[day][slot] = {
                                "subject": tutorial["subject"],
                                "type": "Tutorial",
                                "instructor": ta
                            }
                            if ta in faculty_ta_to_track:
                                faculty_ta_occupancy[day][slot].add(ta)
                            assigned = True
                        attempts += 1

                    if not assigned:
                        print(f"Warning: Could not assign tutorial {tutorial['subject']} for batch {batch}, specialization {spec}.")

                theory_subjects = [sub for sub in self.subjects if sub["type"] == "Theory"]
                subject_counts = {sub["subject"]: 0 for sub in theory_subjects}

                for day in days:
                    lecture_count = 0
                    for slot_index, slot in enumerate(time_slots):
                        if not weekly_schedule[day][slot]:
                            available_subjects = [
                                sub for sub in theory_subjects 
                                if subject_counts[sub["subject"]] < 3 and 
                                sub["subject"] not in [s["subject"] for s in weekly_schedule[day].values() if s] and
                                sub["subject"] not in [s["subject"] for s in weekly_schedule[day].values() if s and s["type"] == "Theory"]
                            ]

                            available_subjects = [
                                sub for sub in available_subjects
                                if not (sub.get("faculty", "N/A") in faculty_ta_to_track and (
                                    sub.get("faculty", "N/A") in faculty_ta_occupancy[day][slot] or
                                    (slot_index > 0 and sub.get("faculty", "N/A") in faculty_ta_occupancy[day][time_slots[slot_index - 1]]) or
                                    (slot_index < len(time_slots) - 1 and sub.get("faculty", "N/A") in faculty_ta_occupancy[day][time_slots[slot_index + 1]])
                                ))
                            ]
                            
                            if available_subjects and lecture_count < 3:
                                subject = random.choice(available_subjects)
                                faculty = subject.get("faculty", "N/A")
                                weekly_schedule[day][slot] = {
                                    "subject": subject["subject"],
                                    "type": "Theory",
                                    "instructor": faculty
                                }
                                subject_counts[subject["subject"]] += 1
                                lecture_count += 1

                                if faculty in faculty_ta_to_track:
                                    faculty_ta_occupancy[day][slot].add(faculty)
                            elif lecture_count >= 3:
                                weekly_schedule[day][slot] = {"subject": "Office Hour", "type": "Office"}

                    if lecture_count < 3:
                        print(f"Warning: Less than 3 lectures assigned on {day} for batch {batch}, specialization {spec}.")

                for day in days:
                    if all(slot is None for slot in weekly_schedule[day].values()):
                        slot = random.choice(time_slots)
                        available_subjects = [
                            sub for sub in theory_subjects if subject_counts[sub["subject"]] < 3
                            if not (sub.get("faculty", "N/A") in faculty_ta_to_track and
                                    sub.get("faculty", "N/A") in faculty_ta_occupancy[day][slot])
                        ]
                        if available_subjects:
                            subject = random.choice(available_subjects)
                            faculty = subject.get("faculty", "N/A")
                            weekly_schedule[day][slot] = {
                                "subject": subject["subject"],
                                "type": "Theory",
                                "instructor": faculty
                            }
                            subject_counts[subject["subject"]] += 1
                            if faculty in faculty_ta_to_track:
                                faculty_ta_occupancy[day][slot].add(faculty)

                for day in days:
                    for slot in time_slots[3:]:
                        if not weekly_schedule[day][slot]:
                            for sub in theory_subjects:
                                if subject_counts[sub["subject"]] < 3:
                                    faculty = sub.get("faculty", "N/A")
                                    if not (faculty in faculty_ta_to_track and faculty in faculty_ta_occupancy[day][slot]):
                                        weekly_schedule[day][slot] = {
                                            "subject": sub["subject"],
                                            "type": "Theory",
                                            "instructor": faculty
                                        }
                                        subject_counts[sub["subject"]] += 1
                                        if faculty in faculty_ta_to_track:
                                            faculty_ta_occupancy[day][slot].add(faculty)
                                        break

                batch_timetable = {
                    "year": self.year,
                    "semester": self.semester,
                    "batch": batch,
                    "specialization": spec,
                    "total_students": total_students,
                    "batch_strength": batch_strength,
                    "data": weekly_schedule
                }
                timetables.append(batch_timetable)

        else:
            for batch in range(1, num_batches + 1):
                weekly_schedule = {day: {slot: None for slot in time_slots} for day in days}

                lab_subjects = [sub for sub in self.subjects if sub["type"] == "Lab"]
                assigned_labs = set()

                for lab in lab_subjects:
                    assigned = False
                    attempts = 0
                    ta = lab.get("ta", "N/A")
                    while not assigned and attempts < 100:
                        day = random.choice(days)
                        slot_index = random.randint(0, len(time_slots) - 2)

                        ta_conflict = (
                            ta in faculty_ta_to_track and
                            (ta in faculty_ta_occupancy[day][time_slots[slot_index]] or
                            ta in faculty_ta_occupancy[day][time_slots[slot_index + 1]])
                        )

                        if (slot_index != 2 and
                            not weekly_schedule[day][time_slots[slot_index]] and 
                            not weekly_schedule[day][time_slots[slot_index + 1]] and
                            not ta_conflict and
                            lab["subject"] not in assigned_labs and
                            not any(s and s.get("type") == "Lab" for s in weekly_schedule[day].values())):
                            
                            weekly_schedule[day][time_slots[slot_index]] = {
                                "subject": lab["subject"],
                                "type": "Lab",
                                "instructor": ta
                            }
                            weekly_schedule[day][time_slots[slot_index + 1]] = {
                                "subject": lab["subject"],
                                "type": "Lab",
                                "instructor": ta
                            }
                            
                            if ta in faculty_ta_to_track:
                                faculty_ta_occupancy[day][time_slots[slot_index]].add(ta)
                                faculty_ta_occupancy[day][time_slots[slot_index + 1]].add(ta)
                            
                            assigned_labs.add(lab["subject"])
                            assigned = True
                        attempts += 1

                    if not assigned:
                        print(f"Warning: Could not assign lab {lab['subject']} for batch {batch}.")

                tutorial_subjects = [sub for sub in self.subjects if sub["type"] == "Tutorial"]

                for tutorial in tutorial_subjects:
                    assigned = False
                    attempts = 0
                    ta = tutorial.get("ta", "N/A")
                    while not assigned and attempts < 100:
                        day = random.choice(days)
                        slot = random.choice(time_slots)

                        ta_conflict = (
                            ta in faculty_ta_to_track and
                            ta in faculty_ta_occupancy[day][slot]
                        )

                        if not weekly_schedule[day][slot] and not ta_conflict:
                            weekly_schedule[day][slot] = {
                                "subject": tutorial["subject"],
                                "type": "Tutorial",
                                "instructor": ta
                            }
                            if ta in faculty_ta_to_track:
                                faculty_ta_occupancy[day][slot].add(ta)
                            assigned = True
                        attempts += 1

                    if not assigned:
                        print(f"Warning: Could not assign tutorial {tutorial['subject']} for batch {batch}.")

                theory_subjects = [sub for sub in self.subjects if sub["type"] == "Theory"]
                subject_counts = {sub["subject"]: 0 for sub in theory_subjects}

                for day in days:
                    lecture_count = 0
                    for slot_index, slot in enumerate(time_slots):
                        if not weekly_schedule[day][slot]:
                            available_subjects = [
                                sub for sub in theory_subjects 
                                if subject_counts[sub["subject"]] < 3 and 
                                sub["subject"] not in [s["subject"] for s in weekly_schedule[day].values() if s] and
                                sub["subject"] not in [s["subject"] for s in weekly_schedule[day].values() if s and s["type"] == "Theory"]
                            ]

                            available_subjects = [
                                sub for sub in available_subjects
                                if not (sub.get("faculty", "N/A") in faculty_ta_to_track and (
                                    sub.get("faculty", "N/A") in faculty_ta_occupancy[day][slot] or
                                    (slot_index > 0 and sub.get("faculty", "N/A") in faculty_ta_occupancy[day][time_slots[slot_index - 1]]) or
                                    (slot_index < len(time_slots) - 1 and sub.get("faculty", "N/A") in faculty_ta_occupancy[day][time_slots[slot_index + 1]])
                                ))
                            ]
                            
                            if available_subjects and lecture_count < 3:
                                subject = random.choice(available_subjects)
                                faculty = subject.get("faculty", "N/A")
                                weekly_schedule[day][slot] = {
                                    "subject": subject["subject"],
                                    "type": "Theory",
                                    "instructor": faculty
                                }
                                subject_counts[subject["subject"]] += 1
                                lecture_count += 1

                                if faculty in faculty_ta_to_track:
                                    faculty_ta_occupancy[day][slot].add(faculty)
                            elif lecture_count >= 3:
                                weekly_schedule[day][slot] = {"subject": "Office Hour", "type": "Office"}

                    if lecture_count < 3:
                        print(f"Warning: Less than 3 lectures assigned on {day} for batch {batch}.")

                for day in days:
                    if all(slot is None for slot in weekly_schedule[day].values()):
                        slot = random.choice(time_slots)
                        available_subjects = [
                            sub for sub in theory_subjects if subject_counts[sub["subject"]] < 3
                            if not (sub.get("faculty", "N/A") in faculty_ta_to_track and
                                    sub.get("faculty", "N/A") in faculty_ta_occupancy[day][slot])
                        ]
                        if available_subjects:
                            subject = random.choice(available_subjects)
                            faculty = subject.get("faculty", "N/A")
                            weekly_schedule[day][slot] = {
                                "subject": subject["subject"],
                                "type": "Theory",
                                "instructor": faculty
                            }
                            subject_counts[subject["subject"]] += 1
                            if faculty in faculty_ta_to_track:
                                faculty_ta_occupancy[day][slot].add(faculty)

                for day in days:
                    for slot in time_slots[3:]:
                        if not weekly_schedule[day][slot]:
                            for sub in theory_subjects:
                                if subject_counts[sub["subject"]] < 3:
                                    faculty = sub.get("faculty", "N/A")
                                    if not (faculty in faculty_ta_to_track and faculty in faculty_ta_occupancy[day][slot]):
                                        weekly_schedule[day][slot] = {
                                            "subject": sub["subject"],
                                            "type": "Theory",
                                            "instructor": faculty
                                        }
                                        subject_counts[sub["subject"]] += 1
                                        if faculty in faculty_ta_to_track:
                                            faculty_ta_occupancy[day][slot].add(faculty)
                                        break

                batch_timetable = {
                    "year": self.year,
                    "semester": self.semester,
                    "batch": batch,
                    "specialization": "None",
                    "total_students": total_students,
                    "batch_strength": batch_strength,
                    "data": weekly_schedule
                }
                timetables.append(batch_timetable)

        self.assign_rooms_and_labs(timetables)

        try:
            for timetable in timetables:
                print(f"Saving timetable entry: {timetable}")
                self.db["timetable"].update_one(
                    {"year": timetable["year"], "semester": timetable["semester"], "batch": timetable["batch"], "specialization": timetable["specialization"]},
                    {"$set": timetable},
                    upsert=True
                )
            print("Timetable generated and updated successfully for all batches!")
        except Exception as e:
            print(f"Error saving timetable to database: {e}")
            return None

        try:
            faculty_ta_occupancy_for_db = {
                day: {slot: list(instructors) for slot, instructors in day_slots.items()}
                for day, day_slots in faculty_ta_occupancy.items()
            }
            faculty_ta_occupancy_collection.update_one(
                {}, {"$set": faculty_ta_occupancy_for_db}, upsert=True
            )
            print("Faculty/TA occupancy updated successfully!")
        except Exception as e:
            print(f"Error saving faculty/TA occupancy: {e}")

        return timetables

    def assign_rooms_and_labs(self, timetables):
        """Assign classrooms and labs to each lecture and lab in the timetable."""
        # Define time slots and days
        time_slots = [
            "9:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30",
            "1:30 - 2:30", "2:30 - 3:30", "3:30 - 4:30", "4:30 - 5:30"
        ]

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        # Fetch room and lab details from the database
        rooms = list(self.db["rooms"].find())
        labs = list(self.db["labs"].find())

        # Debug: Log available rooms and labs
        print(f"Available rooms: {[room for room in rooms]}")
        print(f"Available labs: {[lab for lab in labs]}")

        # Initialize occupancy tracking
        occupancy_collection = self.db["room_lab_occupancy"]
        occupancy = occupancy_collection.find_one() or {day: {slot: {"rooms": [], "labs": []} for slot in time_slots} for day in days}

        for timetable in timetables:
            # Use the pre-calculated batch strength from the timetable
            batch_strength = timetable["batch_strength"]
            print(f"Assigning rooms/labs for batch_strength: {batch_strength}")

            for day, slots in timetable["data"].items():
                for slot_index, slot in enumerate(time_slots):
                    session = slots.get(slot)
                    if session and session["type"] == "Lab":
                        # Ensure two consecutive slots are available in the same lab
                        if slot_index < len(time_slots) - 1:
                            next_slot = time_slots[slot_index + 1]
                            next_session = slots.get(next_slot)
                            if next_session and next_session["type"] == "Lab":
                                assigned_lab = None
                                available_labs = [
                                    lab for lab in labs
                                    if lab.get("strength", 0) >= batch_strength  # Use "strength" for labs
                                    and lab["lab_no"] not in occupancy[day][slot]["labs"]
                                    and lab["lab_no"] not in occupancy[day][next_slot]["labs"]
                                ]
                                print(f"Available labs for {session['subject']} on {day} at {slot}: {available_labs}")
                                if available_labs:
                                    lab = random.choice(available_labs)
                                    assigned_lab = lab["lab_no"]
                                    occupancy[day][slot]["labs"].append(assigned_lab)
                                    occupancy[day][next_slot]["labs"].append(assigned_lab)
                                    session["lab"] = assigned_lab
                                    next_session["lab"] = assigned_lab
                                else:
                                    print(f"Warning: No available lab for {session['subject']} on {day} at {slot} and {next_slot} with capacity >= {batch_strength}.")

                    elif session and session["type"] in ["Theory", "Tutorial"]:
                        # Assign a classroom
                        assigned_room = None
                        available_rooms = [
                            room for room in rooms
                            if room.get("capacity", 0) >= batch_strength
                            and room["room_no"] not in occupancy[day][slot]["rooms"]
                        ]
                        print(f"Available rooms for {session['subject']} on {day} at {slot}: {available_rooms}")
                        if available_rooms:
                            room = random.choice(available_rooms)
                            assigned_room = room["room_no"]
                            occupancy[day][slot]["rooms"].append(assigned_room)
                            session["room"] = assigned_room
                        else:
                            print(f"Warning: No available room for {session['subject']} on {day} at {slot} with capacity >= {batch_strength}.")

        # Update the occupancy collection
        occupancy_collection.update_one(
            {},
            {"$set": occupancy},
            upsert=True
        )






       
               







