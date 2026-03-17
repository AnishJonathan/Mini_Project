import sqlite3
import re
import os

schema = """
CREATE TABLE `admin` (
  `A_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `L_name` varchar(250) NOT NULL,
  `M_name` varchar(250) NOT NULL,
  `F_name` varchar(250) NOT NULL,
  `A_email` text NOT NULL,
  `A_pass` text NOT NULL,
  `dept` text NOT NULL,
  `A_num` varchar(10) NOT NULL,
  `A_gender` varchar(1) NOT NULL,
  `img` text NOT NULL,
  `first_login` INTEGER DEFAULT 1,
  `otp_used` INTEGER DEFAULT 1
);

CREATE TABLE `department` (
  `dept_id` varchar(20) PRIMARY KEY,
  `dept_name` varchar(70) NOT NULL,
  `dept_short` varchar(20) NOT NULL,
  `dept_intake` INTEGER NOT NULL,
  `dept_seat_filled` INTEGER NOT NULL,
  `duration` INTEGER NOT NULL
);

CREATE TABLE `faculty` (
  `F_id` INTEGER PRIMARY KEY,
  `Designation` text,
  `L_name` text NOT NULL,
  `F_name` text NOT NULL,
  `M_name` text NOT NULL,
  `F_email` text NOT NULL,
  `F_password` text NOT NULL,
  `dept` text NOT NULL,
  `F_num` varchar(10) NOT NULL,
  `gender` varchar(1) NOT NULL,
  `img` text NOT NULL,
  `first_login` INTEGER DEFAULT 1,
  `otp_used` INTEGER DEFAULT 1
);

CREATE TABLE `questions` (
  `q_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `q_no` INTEGER NOT NULL,
  `question` text NOT NULL,
  `ans_type` INTEGER DEFAULT NULL,
  `opt1` text,
  `opt2` text,
  `opt3` text,
  `opt4` text,
  `correct_opt` text,
  `q_time` text NOT NULL,
  `points` INTEGER DEFAULT NULL,
  `quiz_id` text NOT NULL
);

CREATE TABLE `quiz_det` (
  `quiz_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `q_title` text NOT NULL,
  `q_dept` text NOT NULL,
  `q_sem` text NOT NULL,
  `q_sub` text,
  `q_batch` text NOT NULL,
  `q_date` text NOT NULL,
  `quiz_type` varchar(1) DEFAULT NULL,
  `q_timer` INTEGER DEFAULT NULL,
  `q_time_start` text NOT NULL,
  `q_time_end` text NOT NULL,
  `q_time_division` text NOT NULL,
  `show_answer` INTEGER NOT NULL,
  `fac_inserted` text NOT NULL,
  `switch_limit` INTEGER NOT NULL DEFAULT 5,
  `desc_time` INTEGER NOT NULL DEFAULT 0,
  `quiz_status` INTEGER DEFAULT 0,
  `quiz_started` INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE `quiz_responses` (
  `response_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `one_line_ans` text,
  `selected_opt` text,
  `desc_ans_name` varchar(250) DEFAULT NULL,
  `desc_ans_file` varchar(250) DEFAULT NULL,
  `ques_type` text NOT NULL,
  `quiz_start` text NOT NULL,
  `time_per_ques` text NOT NULL,
  `user_inserted` text NOT NULL,
  `ques_id` text NOT NULL,
  `quiz_id` text NOT NULL
);

CREATE TABLE `score` (
  `score_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `user` text NOT NULL,
  `username` text,
  `roll` text,
  `user_score` text NOT NULL,
  `total_points` text NOT NULL,
  `ques_points` text NOT NULL,
  `total_time_taken` text,
  `time_submitted` text NOT NULL,
  `quiz_id` text NOT NULL,
  `quiz_attempted` text NOT NULL,
  `stud_img` text,
  `pending_chk` INTEGER NOT NULL
);

-- Note: student has 20 columns in MySQL schema but INSERTs have 19 values. Defaulting first_login
CREATE TABLE `student` (
  `S_id` varchar(10) PRIMARY KEY,
  `S_pass` text NOT NULL,
  `L_name` text NOT NULL,
  `F_name` text NOT NULL,
  `M_name` text NOT NULL,
  `roll` INTEGER NOT NULL,
  `batch` INTEGER NOT NULL,
  `S_email` text NOT NULL,
  `KT` INTEGER NOT NULL,
  `Type` INTEGER DEFAULT NULL,
  `S_num` varchar(10) NOT NULL,
  `P_email` text NOT NULL,
  `P_num` varchar(10) NOT NULL,
  `current_sem` INTEGER NOT NULL,
  `image` text NOT NULL,
  `gender` varchar(1) NOT NULL,
  `dept` text,
  `elective1` text,
  `elective2` text,
  `first_login` INTEGER DEFAULT 1,
  `otp_used` INTEGER DEFAULT 1
);

CREATE TABLE `subject` (
  `u_key` INTEGER PRIMARY KEY AUTOINCREMENT,
  `course_code` varchar(20) NOT NULL,
  `sub_name_short` varchar(30) NOT NULL,
  `sem` varchar(20) NOT NULL,
  `F_id` INTEGER NOT NULL,
  `year` INTEGER NOT NULL,
  `sub_type` INTEGER NOT NULL,
  `is_elective` INTEGER NOT NULL,
  `elective_of` INTEGER NOT NULL,
  `marks` INTEGER NOT NULL,
  `dept_id` varchar(20) NOT NULL
);
CREATE TABLE `electives` (
  `course_code` varchar(20) NOT NULL,
  `sub_name_long` text NOT NULL,
  `sub_name_short` varchar(30) NOT NULL,
  `sem` varchar(5) NOT NULL,
  `sub_type` int NOT NULL DEFAULT '1',
  `elective_category` int DEFAULT NULL,
  `marks` int NOT NULL DEFAULT '0',
  `dept_id` varchar(20) NOT NULL,
  PRIMARY KEY (`course_code`,`sem`)
);

CREATE TABLE `electives_category` (
  `category_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `cat_name` varchar(50) NOT NULL,
  `sem` varchar(5) NOT NULL,
  `dept_id` varchar(10) NOT NULL
);
"""

def main():
    import os
    db_file = 'examportal.db'
    if os.path.exists(db_file):
        os.remove(db_file)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 1. Create tables
    cursor.executescript(schema)

    # 2. Read test_wise.sql and extract INSERT statements robustly
    with open('test_wise.sql', 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Strip MySQL conditional comments like /*!40000 ... */;
    content = re.sub(r'/\*!.*?\*/', '', content, flags=re.DOTALL)

    statements = []
    lines = content.splitlines()
    current_stmt = []
    in_stmt = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('--') or stripped.startswith('/*'):
            continue
            
        su = stripped.upper()
        # Skip MySQL directives
        if su.startswith('LOCK TABLES') or su.startswith('UNLOCK TABLES') or \
           su.startswith('ALTER TABLE') or su.startswith('SET ') or \
           su.startswith('DROP TABLE') or su.startswith('CREATE TABLE'):
            continue
            
        if su.startswith('INSERT INTO'):
            in_stmt = True
            current_stmt = [stripped]
        elif in_stmt:
            current_stmt.append(stripped)
            
        if in_stmt and stripped.endswith(';'):
            stmt = " ".join(current_stmt)
            # Remove backticks for SQLite compatibility
            stmt = stmt.replace('`', '')
            statements.append(stmt)
            current_stmt = []
            in_stmt = False

    # 3. Execute INSERT statements
    from werkzeug.security import generate_password_hash
    
    for stmt in statements:
        # Check if this is an insert into admin, faculty, or student to hash passwords
        if 'INSERT INTO admin' in stmt or 'INSERT INTO faculty' in stmt or 'INSERT INTO student' in stmt:
            try:
                # Basic parsing to extract values
                # Looking for VALUES (...) pattern
                values_match = re.search(r'VALUES\s+(.*);', stmt, re.IGNORECASE | re.DOTALL)
                if values_match:
                    prefix = stmt[:values_match.start(1)]
                    values_part = values_match.group(1)
                    
                    # Split rows by '),(' but be careful about commas inside strings
                    # For this dump, we can split by '),(' and then fix the start/end
                    rows_raw = values_part.split('),(')
                    hashed_rows = []
                    
                    for i, row in enumerate(rows_raw):
                        cleaned_row = row.strip()
                        if cleaned_row.startswith('('): cleaned_row = cleaned_row[1:]
                        if cleaned_row.endswith(')'): cleaned_row = cleaned_row[:-1]
                        
                        # Split by comma but ignore commas inside single quotes
                        # Simple csv-like split for SQL values
                        vals = []
                        current_val = []
                        in_quotes = False
                        for char in cleaned_row:
                            if char == "'" and (not current_val or current_val[-1] != "\\"):
                                in_quotes = not in_quotes
                                current_val.append(char)
                            elif char == "," and not in_quotes:
                                vals.append("".join(current_val).strip())
                                current_val = []
                            else:
                                current_val.append(char)
                        vals.append("".join(current_val).strip())
                        
                        # admin: pass is at index 5 (A_pass)
                        # faculty: pass is at index 6 (F_password)
                        # student: pass is at index 1 (S_pass)
                        def unquote(s):
                            s = s.strip()
                            if s.startswith("'") and s.endswith("'"): return s[1:-1]
                            return s

                        if 'INSERT INTO admin' in stmt:
                            raw_pass = unquote(vals[5])
                            vals[5] = f"'{generate_password_hash(raw_pass)}'"
                            # Append first_login and otp_used
                            vals.append('1')
                            vals.append('1')
                        elif 'INSERT INTO faculty' in stmt:
                            raw_pass = unquote(vals[6])
                            vals[6] = f"'{generate_password_hash(raw_pass)}'"
                            # Append first_login and otp_used
                            vals.append('1')
                            vals.append('1')
                        elif 'INSERT INTO student' in stmt:
                            raw_pass = unquote(vals[1])
                            vals[1] = f"'{generate_password_hash(raw_pass)}'"
                            # Append first_login and otp_used
                            vals.append('1')
                            vals.append('1')
                        
                        hashed_rows.append(f"({','.join(vals)})")
                    
                    stmt = f"{prefix}{','.join(hashed_rows)};"
            except Exception as e:
                print(f"Password hashing failed for stmt, executing as is: {e}")

        try:
            cursor.execute(stmt)
        except Exception as e:
            print(f"Failed to execute: {stmt[:100]}...")
            print(f"Error: {e}")

    # 4. Post-migration: Data Consistency for App Compatibility
    try:
        cursor.execute("ALTER TABLE subject ADD COLUMN sub_name_long TEXT")
        cursor.execute("UPDATE subject SET sub_name_long = sub_name_short WHERE sub_name_long IS NULL")
    except Exception as e:
        print(f"Post-migration step failed: {e}")

    conn.commit()
    conn.close()
    print(f"Migration finished successfully! Total inserts: {len(statements)}")

if __name__ == "__main__":
    main()
