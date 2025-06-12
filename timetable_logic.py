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

    def __init__(self, year, semester ,specialization=None):
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
            if self.specialization:  # Only add if not empty
                query["specialization"] = self.specialization

            print(f"Fetching subjects with query: {query}")

            self.subjects = list(self.db["Subject_collection"].find(query))

            if not self.subjects:
                raise ValueError(f"No subjects found for {year_str} - {semester_str} with specialization {self.specialization or 'None'}.")

            if not self.rooms:
                raise ValueError("No rooms found in the database.")

        except Exception as e:
            print(f"Error fetching data: {e}")
            return False

        return True



    def generate_timetable(self):
        """Generate and save the timetable ensuring no faculty conflicts between batches."""
        if not self.fetch_data():
            print("Failed to generate timetable due to missing data.")
            return None

        strength_info = self.db["strength_details"].find_one({"year": str(self.year)})

        if not strength_info or "sections" not in strength_info:
            print(f"No section details found for year {self.year}.")
            return None

        num_batches = int(strength_info["sections"])

        time_slots = [
            "9:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30",
            "1:30 - 2:30", "2:30 - 3:30", "3:30 - 4:30", "4:30 - 5:30"
        ]

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        global_faculty_schedule = {day: {slot: None for slot in time_slots} for day in days}

        timetables = []

        for batch in range(1, num_batches + 1):
            weekly_schedule = {day: {slot: None for slot in time_slots} for day in days}

            lab_subjects = [sub for sub in self.subjects if sub["type"] == "Lab"]
            assigned_labs = set()

            # Ensure all labs are assigned
            for lab in lab_subjects:
                assigned = False
                attempts = 0
                while not assigned and attempts < 100:  # Further increase attempts
                    day = random.choice(days)
                    slot_index = random.randint(0, len(time_slots) - 2)

                    if (slot_index != 2 and
                        not weekly_schedule[day][time_slots[slot_index]] and 
                        not weekly_schedule[day][time_slots[slot_index + 1]] and
                        not global_faculty_schedule[day][time_slots[slot_index]] and
                        not global_faculty_schedule[day][time_slots[slot_index + 1]] and
                        lab["subject"] not in assigned_labs and
                        not any(s and s.get("type") == "Lab" for s in weekly_schedule[day].values())):
                        
                        weekly_schedule[day][time_slots[slot_index]] = {"subject": lab["subject"], "type": "Lab"}
                        weekly_schedule[day][time_slots[slot_index + 1]] = {"subject": lab["subject"], "type": "Lab"}
                        
                        global_faculty_schedule[day][time_slots[slot_index]] = lab["subject"]
                        global_faculty_schedule[day][time_slots[slot_index + 1]] = lab["subject"]
                        
                        assigned_labs.add(lab["subject"])
                        assigned = True
                    attempts += 1

                if not assigned:
                    print(f"Warning: Could not assign lab {lab['subject']} for batch {batch}.")

            tutorial_subjects = [sub for sub in self.subjects if sub["type"] == "Tutorial"]

            # Ensure all tutorials are assigned
            for tutorial in tutorial_subjects:
                assigned = False
                attempts = 0
                while not assigned and attempts < 100:  # Further increase attempts
                    day = random.choice(days)
                    slot = random.choice(time_slots)
                    if not weekly_schedule[day][slot] and not global_faculty_schedule[day][slot]:
                        weekly_schedule[day][slot] = {"subject": tutorial["subject"], "type": "Tutorial"}
                        global_faculty_schedule[day][slot] = tutorial["subject"]
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
                            global_faculty_schedule[day][slot] != sub["subject"] and
                            sub["subject"] not in [s["subject"] for s in weekly_schedule[day].values() if s] and
                            (slot_index == 0 or global_faculty_schedule[day][time_slots[slot_index - 1]] != sub["subject"]) and
                            (slot_index == len(time_slots) - 1 or global_faculty_schedule[day][time_slots[slot_index + 1]] != sub["subject"]) and
                            sub["subject"] not in [s["subject"] for s in weekly_schedule[day].values() if s and s["type"] == "Theory"]
                        ]
                        
                        if available_subjects and lecture_count < 3:
                            subject = random.choice(available_subjects)
                            weekly_schedule[day][slot] = {"subject": subject["subject"], "type": "Theory"}
                            subject_counts[subject["subject"]] += 1
                            lecture_count += 1

                            global_faculty_schedule[day][slot] = subject["subject"]
                        elif lecture_count >= 3:
                            weekly_schedule[day][slot] = {"subject": "Office Hour", "type": "Office"}

                if lecture_count < 3:
                    print(f"Warning: Less than 3 lectures assigned on {day} for batch {batch}.")

            # Ensure at least one lecture per day
            for day in days:
                if all(slot is None for slot in weekly_schedule[day].values()):
                    slot = random.choice(time_slots)
                    subject = random.choice(theory_subjects)
                    weekly_schedule[day][slot] = {"subject": subject["subject"], "type": "Theory"}
                    subject_counts[subject["subject"]] += 1

            # Fill remaining slots with unassigned subjects, prioritizing after lunch
            for day in days:
                for slot in time_slots[3:]:  # Start filling from after lunch
                    if not weekly_schedule[day][slot]:
                        for sub in theory_subjects:
                            if subject_counts[sub["subject"]] < 3:
                                weekly_schedule[day][slot] = {"subject": sub["subject"], "type": "Theory"}
                                subject_counts[sub["subject"]] += 1
                                break

            batch_timetable = {
                "year": self.year,
                "semester": self.semester,
                "batch": batch,
                "data": weekly_schedule
            }
            timetables.append(batch_timetable)

        # Assign rooms and labs to the generated timetable
        self.assign_rooms_and_labs(timetables)

        # Save the timetable with room and lab assignments to the database
        try:
            for timetable in timetables:
                self.db["timetable"].update_one(
                    {"year": timetable["year"], "semester": timetable["semester"], "batch": timetable["batch"]},
                    {"$set": timetable},
                    upsert=True
                )
            print("Timetable generated and updated successfully for all batches!")
            return timetables
        except Exception as e:
            print(f"Error saving timetable to database: {e}")
            return None

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

        # Fetch strength details
        strength_info = self.db["strength_details"].find_one({"year": str(self.year)})
        if not strength_info:
            print(f"No strength details found for year {self.year}.")
            return None

        total_strength = strength_info.get("total_strength", 0)
        num_batches = int(strength_info["sections"])
        batch_strength = round(total_strength / num_batches)

        # Initialize or fetch occupancy tracking
        occupancy_collection = self.db["room_lab_occupancy"]
        occupancy = occupancy_collection.find_one() or {day: {slot: {"rooms": [], "labs": []} for slot in time_slots} for day in days}

        for timetable in timetables:
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
                                for lab in labs:
                                    if (lab["strength"] >= batch_strength and
                                        lab["lab_no"] not in occupancy[day][slot]["labs"] and
                                        lab["lab_no"] not in occupancy[day][next_slot]["labs"]):
                                        assigned_lab = lab["lab_no"]
                                        occupancy[day][slot]["labs"].append(assigned_lab)
                                        occupancy[day][next_slot]["labs"].append(assigned_lab)
                                        break
                                if assigned_lab:
                                    session["lab"] = assigned_lab
                                    next_session["lab"] = assigned_lab
                                else:
                                    print(f"Warning: No available lab for {session['subject']} on {day} at {slot} and {next_slot}.")

                    elif session and session["type"] in ["Theory", "Tutorial"]:
                        # Assign a classroom
                        assigned_room = None
                        for room in rooms:
                            if room["capacity"] >= batch_strength and room["room_no"] not in occupancy[day][slot]["rooms"]:
                                assigned_room = room["room_no"]
                                occupancy[day][slot]["rooms"].append(assigned_room)
                                break
                        if assigned_room:
                            session["room"] = assigned_room
                        else:
                            print(f"Warning: No available room for {session['subject']} on {day} at {slot}.")

        # Update the occupancy collection
        occupancy_collection.update_one(
            {},
            {"$set": occupancy},
            upsert=True
        )








       
               







