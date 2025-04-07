from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton,QMessageBox
from PyQt6.QtCore import pyqtSignal
import pymongo,random
import traceback


class TimetableDialog(QDialog):
    timetable_generated = pyqtSignal()  # Signal to indicate timetable generation

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Year and Semester")

        layout = QVBoxLayout()

        # Year Selection
        self.year_label = QLabel("Select Year:")
        self.year_combo = QComboBox()
        self.year_combo.addItems(["1st Year", "2nd Year", "3rd Year", "4th Year"])
        layout.addWidget(self.year_label)
        layout.addWidget(self.year_combo)

        # Semester Selection (Dynamically Updates)
        self.sem_label = QLabel("Select Semester:")
        self.sem_combo = QComboBox()
        self.update_semesters(0)  # Initialize with first year's semesters
        layout.addWidget(self.sem_label)
        layout.addWidget(self.sem_combo)

        # Generate Button
        self.generate_button = QPushButton("Generate Timetable")
        self.generate_button.clicked.connect(self.generate_timetable)
        layout.addWidget(self.generate_button)

        self.setLayout(layout)

        # Connect signals
        self.year_combo.currentIndexChanged.connect(self.update_semesters)

    def update_semesters(self, index):
        """Update semester options based on selected year."""
        year_semesters = {
            0: ["1st Semester", "2nd Semester"],  # 1st Year
            1: ["3rd Semester", "4th Semester"],  # 2nd Year
            2: ["5th Semester", "6th Semester"],  # 3rd Year
            3: ["7th Semester", "8th Semester"]   # 4th Year
        }

        self.sem_combo.clear()
        self.sem_combo.addItems(year_semesters.get(index, []))

    def get_selected_year_sem(self):
        """Return selected year and semester in integer format"""
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
        return selected_year, selected_sem

    def generate_timetable(self):
        """Trigger timetable generation when button is clicked"""
        year, semester = self.get_selected_year_sem()  # Get year & semester as integers

        try:
            generator = TimetableGenerator(year, semester)
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

    def __init__(self, year, semester):
        self.year = year
        self.semester = semester
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["timetable_db"]
        self.timetable = {}

    def fetch_data(self):
        """Fetch all required data from the database with proper formatting and error handling."""
        try:
            self.rooms = list(self.db["rooms"].find())
            self.labs = list(self.db["labs"].find())

            # Convert year to match DB format (e.g., "1st Year" instead of "1 Year")
            year_map = {
                "1": "1st Year",
                "2": "2nd Year",
                "3": "3rd Year",
                "4": "4th Year"
            }
            year_str = year_map.get(str(self.year), f"{self.year} Year")  # Handle unexpected input

            # Convert semester (should be correct as "Semester 1", "Semester 2", etc.)
            semester_str = f"Semester {self.semester}"

            # Fetch subjects (subjects now contain faculty details)
            self.subjects = list(self.db["Subject_collection"].find({"year": year_str, "semester": semester_str}))

            # Error handling
            if not self.subjects:
                raise ValueError(f"No subjects found for {year_str} - {semester_str}.")
            if not self.rooms:
                raise ValueError("No rooms found in the database.")

        except Exception as e:
            print(f"Error fetching data: {e}")
            return False  # Indicate failure
        
        return True  # Indicate success

    def assign_subjects(self):
        """Assign subjects including Theory and Lab, ensuring unique storage in a MongoDB-friendly format."""
        try:
            semester_key = str(self.semester)  # Convert semester to string
            self.timetable[semester_key] = []  # Use string key for MongoDB
            
            for subject in self.subjects:
                self.timetable[semester_key].append({
                    "subject": subject["subject"],
                    "type": subject["type"],  # Store Theory/Lab distinction
                    "faculty": subject["faculty"]  # Store faculty from Subject_collection
                })

            print(f"Subjects assigned successfully for Semester {self.semester}")

        except Exception as e:
            print(f"Error assigning subjects: {e}")

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

        # Initialize occupancy tracking
        occupancy = {day: {slot: {"rooms": [], "labs": []} for slot in time_slots} for day in days}

        for timetable in timetables:
            for day, slots in timetable["data"].items():
                for slot, session in slots.items():
                    if session:
                        if session["type"] == "Lab":
                            # Assign a lab
                            assigned_lab = None
                            for lab in labs:
                                if lab["strength"] >= batch_strength and lab["lab_no"] not in occupancy[day][slot]["labs"]:
                                    assigned_lab = lab["lab_no"]
                                    occupancy[day][slot]["labs"].append(assigned_lab)
                                    break
                            if assigned_lab:
                                session["lab"] = assigned_lab
                            else:
                                print(f"Warning: No available lab for {session['subject']} on {day} at {slot}.")

                        elif session["type"] in ["Theory", "Tutorial"]:
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









       
               







