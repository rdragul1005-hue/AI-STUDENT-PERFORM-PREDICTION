import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, abort, flash, g, jsonify, redirect, render_template, request, session, url_for


ROOT = Path(__file__).resolve().parent
DATABASE = ROOT / "student_performance.db"

COURSES = {
    "c": {
        "name": "C Programming",
        "short": "C",
        "icon": "C",
        "color": "coral",
        "description": "Build a strong foundation in structured programming.",
        "lessons": [
            ("Getting started with C", "C is a compiled, procedural language. A C program begins execution in main. The preprocessor handles directives such as #include before compilation, and the compiler turns your source into an executable.", " #include <stdio.h>\n\nint main(void) {\n    printf(\"Hello, world!\\\\n\");\n    return 0;\n}"),
            ("Variables and data types", "Variables give names to values stored in memory. C has fundamental types such as int, char, float, and double. Choose a type that fits the data, initialize variables before reading them, and use format specifiers that match their types.", "int year = 2026;\nfloat temperature = 24.5f;\nchar grade = 'A';\nprintf(\"%d %.1f %c\\\\n\", year, temperature, grade);"),
            ("Operators and expressions", "Arithmetic, relational, and logical operators combine values into expressions. Integer division discards the fractional part. Use parentheses to make evaluation order clear, and use && or || to combine conditions.", "int total = 17 + 5;\nint remainder = total % 4;\nint eligible = total >= 20 && remainder == 2;"),
            ("Decisions and loops", "Use if and else to choose between paths. A for loop is useful when the number of repetitions is known; while repeats while a condition remains true. Check loop boundaries carefully to avoid off-by-one errors.", "for (int number = 1; number <= 5; number++) {\n    printf(\"%d\\\\n\", number);\n}"),
            ("Functions and arrays", "Functions package reusable work behind a name and parameter list. Arrays store a fixed-size sequence of one type, with indexes starting at zero. Pass an array's length when a function needs to iterate safely.", "int sum(const int values[], int length) {\n    int result = 0;\n    for (int i = 0; i < length; i++) result += values[i];\n    return result;\n}"),
        ],
        "practice": [
            "Write and compile a complete program that prints your name, course, and one learning goal on separate lines. Include the required header and return a success status from main.",
            "Build a student profile program with variables for a name, register number, and semester. Print all three with the correct printf format specifiers.",
            "Read two integers and print their sum, product, and remainder. Try a negative value too, then explain why integer division behaves differently from decimal division.",
            "Ask for a student's mark and use if/else to print Pass or Needs practice. Extend it with a loop that checks marks for five students.",
            "Store five quiz marks in an array, write a function that calculates their total and average, and print the highest mark.",
        ],
        "quiz": [
            ("Which function is the entry point of a standard C program?", ["start()", "main()", "run()", "init()"], 1),
            ("Which header declares printf?", ["<stdlib.h>", "<string.h>", "<stdio.h>", "<math.h>"], 2),
            ("Which type stores a whole number?", ["int", "float", "char*", "double"], 0),
            ("What is the index of the first element in a C array?", ["1", "-1", "It depends", "0"], 3),
            ("Which operator gives the remainder?", ["/", "%", "//", "&"], 1),
            ("Which keyword returns a value from a function?", ["break", "continue", "return", "yield"], 2),
            ("How many times does `for (int i=0; i<3; i++)` run?", ["2", "3", "4", "0"], 1),
            ("Which symbol ends a C statement?", [".", ":", ";", ","], 2),
            ("What does `&&` mean?", ["Logical AND", "Logical OR", "Bitwise NOT", "Assignment"], 0),
            ("Which is a character literal?", ["\"A\"", "'A'", "`A`", "(A)"], 1),
        ],
    },
    "cpp": {
        "name": "C++ Programming",
        "short": "C++",
        "icon": "++",
        "color": "blue",
        "description": "Explore modern C++ and object-oriented programming.",
        "lessons": [
            ("Getting started with C++", "C++ supports procedural, object-oriented, and generic programming. A typical program includes the iostream library and writes output with std::cout. The main function returns an integer status to the operating system.", "#include <iostream>\n\nint main() {\n    std::cout << \"Hello, C++!\\\\n\";\n    return 0;\n}"),
            ("Types and variables", "C++ offers built-in types and library types. Use const for values that should not change, and prefer clear initialization with braces. The auto keyword asks the compiler to infer a variable's type from its initializer.", "const int attempts{3};\nauto message = std::string{\"Ready\"};\nbool complete{false};"),
            ("Conditions and iteration", "if and switch express decisions. Range-based for loops make it easy to visit every element in a collection. Use references when you need to modify elements without copying them.", "for (const auto& language : languages) {\n    std::cout << language << '\\\\n';\n}"),
            ("Functions and classes", "Functions can be overloaded when their parameter lists differ. Classes group data and behavior; public members form the interface, while private members protect implementation details. Constructors establish valid initial state.", "class Course {\npublic:\n    Course(std::string title) : title_{title} {}\n    std::string title() const { return title_; }\nprivate:\n    std::string title_;\n};"),
            ("STL containers and algorithms", "The standard library provides containers such as vector and map, plus reusable algorithms. A vector grows dynamically. Iterators connect containers to algorithms such as std::sort, reducing the need to write common loops yourself.", "std::vector<int> scores{8, 5, 10};\nstd::sort(scores.begin(), scores.end());"),
        ],
        "practice": [
            "Create a complete C++ program that prints a small welcome message and a numbered list of three topics using std::cout.",
            "Create a course summary with const values for the course name and lesson count. Use auto for a message that combines the values, then print it.",
            "Put five marks in a vector and use a range-based loop to print each mark and calculate the total.",
            "Define a Student class with a private name and register number, a constructor, and a public method that prints a student summary.",
            "Read several marks into a vector, sort them with std::sort, and display the sorted list and its median.",
        ],
        "quiz": [
            ("Which stream is commonly used for console output in C++?", ["std::cout", "std::cin", "std::print", "std::out"], 0),
            ("Which header provides std::vector?", ["<array>", "<vector>", "<list.h>", "<container>"], 1),
            ("What does `const` indicate for a variable?", ["It is global", "It cannot be changed through that name", "It is temporary", "It is private"], 1),
            ("Which loop visits each element in a container?", ["Range-based for", "do-until", "foreach()", "repeat"], 0),
            ("Which access label hides class implementation details?", ["public", "open", "private", "visible"], 2),
            ("Which standard algorithm sorts a range?", ["std::order", "std::sort", "std::arrange", "std::sequence"], 1),
            ("What is a constructor used for?", ["Destroying an object", "Initializing an object", "Sorting a class", "Including a header"], 1),
            ("Which keyword can infer a variable's type?", ["var", "let", "auto", "infer"], 2),
            ("What does `std::cin` typically do?", ["Read input", "Print output", "Sort values", "Allocate a vector"], 0),
            ("What does STL stand for?", ["Standard Template Library", "Simple Type List", "System Transfer Link", "Source Text Language"], 0),
        ],
    },
    "java": {
        "name": "Java Programming",
        "short": "Java",
        "icon": "J",
        "color": "amber",
        "description": "Learn object-oriented Java and the JVM ecosystem.",
        "lessons": [
            ("Java and your first program", "Java source is compiled to bytecode and run by the Java Virtual Machine. A class groups related code, and the main method is the conventional starting point for an application.", "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, Java!\");\n    }\n}"),
            ("Variables and types", "Java is statically typed: each variable has a declared type. Primitive types include int, double, and boolean; String is an object. Use descriptive names and initialize values before using them.", "int lessons = 5;\ndouble hours = 1.5;\nString learner = \"Asha\";\nboolean passed = true;"),
            ("Conditions and loops", "Use if/else to branch and for or while loops to repeat work. A for-each loop is concise when visiting every item in an array or collection. Braces make the scope of each block explicit.", "for (String topic : topics) {\n    System.out.println(topic);\n}"),
            ("Methods and classes", "Methods define operations and may accept parameters and return a value. Classes define state and behavior. Encapsulation keeps fields private and exposes intentional operations through methods or constructors.", "class Student {\n    private final String name;\n    Student(String name) { this.name = name; }\n    String getName() { return name; }\n}"),
            ("Collections and exceptions", "The Java Collections Framework includes List, Set, and Map interfaces. ArrayList is a resizable list. Exceptions represent errors or unusual conditions; use try/catch when your code can recover meaningfully.", "List<Integer> marks = new ArrayList<>();\nmarks.add(9);\ntry {\n    System.out.println(marks.get(0));\n} catch (IndexOutOfBoundsException error) {\n    System.out.println(\"No mark yet\");\n}"),
        ],
        "practice": [
            "Write a complete Main class that prints a welcome message, your course name, and a short daily learning goal.",
            "Create variables for a student's name, register number, and average mark. Print a formatted student profile and try changing the values.",
            "Ask the user for a mark with Scanner and use if/else to classify it as Pass or Needs practice. Loop through three sample marks.",
            "Create a Student class with private name and register-number fields, initialize them in a constructor, and add a method that returns a summary.",
            "Store quiz marks in an ArrayList, calculate their average, and handle an empty list without trying to divide by zero.",
        ],
        "quiz": [
            ("What runs Java bytecode?", ["Java Virtual Machine", "C compiler", "Browser engine", "Database"], 0),
            ("Which is the standard Java program entry method?", ["start()", "public static void main(String[] args)", "run(String)", "init()"], 1),
            ("Which type represents true or false?", ["int", "String", "boolean", "char"], 2),
            ("Which keyword creates an object?", ["make", "new", "class", "this"], 1),
            ("Which collection is a resizable ordered list?", ["HashSet", "ArrayList", "TreeMap", "Queue"], 1),
            ("Which access modifier generally hides a field?", ["public", "private", "static", "final"], 1),
            ("Which block handles an exception?", ["if", "catch", "loop", "throws"], 1),
            ("Which keyword declares a class that cannot be subclassed?", ["static", "private", "final", "const"], 2),
            ("What does `System.out.println` do?", ["Reads a file", "Prints a line", "Creates a class", "Stops the JVM"], 1),
            ("Which loop is designed to visit each item in a collection?", ["for-each", "switch", "while-each", "case"], 0),
        ],
    },
    "html": {
        "name": "HTML",
        "short": "HTML",
        "icon": "5",
        "color": "orange",
        "description": "Structure accessible, meaningful web pages.",
        "lessons": [
            ("The structure of a web page", "HTML describes the structure and meaning of web content. A document includes a doctype, an html root, metadata in head, and visible content in body. Use semantic elements to communicate the purpose of each region.", "<!doctype html>\n<html lang=\"en\">\n  <head><meta charset=\"utf-8\"><title>My page</title></head>\n  <body><h1>Welcome</h1></body>\n</html>"),
            ("Text and semantic elements", "Headings organize content hierarchically, paragraphs contain text, and lists group related items. Semantic elements such as main, article, and nav make page structure easier to understand for people and assistive technologies.", "<main>\n  <h1>Study plan</h1>\n  <p>Practice a little every day.</p>\n  <ul><li>Read</li><li>Build</li></ul>\n</main>"),
            ("Links and images", "The anchor element links to another resource with href. Images use src and concise alternative text in alt so the information is available when images cannot be seen. Use meaningful link labels that make sense out of context.", "<a href=\"/materials/html\">Continue learning</a>\n<img src=\"campus.jpg\" alt=\"Students at the campus entrance\">"),
            ("Forms and inputs", "Forms collect user input. Associate each label with an input using matching for and id values. Choose an input type that matches the data and provide required constraints so users can correct mistakes.", "<form>\n  <label for=\"email\">Email</label>\n  <input id=\"email\" name=\"email\" type=\"email\" required>\n  <button type=\"submit\">Join</button>\n</form>"),
            ("Tables and accessibility", "Use tables for genuinely tabular data, not for layout. Give tables a caption and header cells. Keep document language set, preserve a logical heading order, and ensure interactive controls have accessible names.", "<table>\n  <caption>Quiz results</caption>\n  <tr><th scope=\"col\">Course</th><th scope=\"col\">Mark</th></tr>\n  <tr><td>HTML</td><td>9 / 10</td></tr>\n</table>"),
        ],
        "practice": [
            "Create a complete HTML page for a student portfolio with a title, language attribute, metadata, one main heading, and a short introduction.",
            "Build a semantic weekly study plan with a main region, a section for each day, and an ordered list of that day's learning activities.",
            "Create a course resource page with links to three lessons and an image. Give the image descriptive alternative text and make each link label meaningful.",
            "Build a registration form with labeled name and register-number fields, appropriate input types, and required-field validation.",
            "Create an accessible quiz-results table with a caption, column headers, and at least three student rows. Check that the header scopes and heading order are meaningful.",
        ],
        "quiz": [
            ("What does HTML primarily describe?", ["Page structure and meaning", "Database queries", "Server hardware", "Image editing"], 0),
            ("Which element is the main page heading?", ["<head>", "<h1>", "<title>", "<header-text>"], 1),
            ("Where does visible page content belong?", ["<meta>", "<body>", "<style>", "<script>"], 1),
            ("Which attribute sets a link destination?", ["src", "alt", "href", "action"], 2),
            ("What is the purpose of image alt text?", ["Set image size", "Describe the image for accessibility", "Load a font", "Create a link"], 1),
            ("Which element labels a form control?", ["<label>", "<legend-text>", "<caption>", "<name>"], 0),
            ("Which element is appropriate for a bulleted list?", ["<ol>", "<ul>", "<dl>", "<li-group>"], 1),
            ("Which element represents a page's primary content?", ["<main>", "<aside>", "<footer>", "<small>"], 0),
            ("What is a semantic HTML element?", ["An element that conveys meaning", "Any element with a style", "An image format", "A JavaScript function"], 0),
            ("Which element is designed to contain tabular data?", ["<grid>", "<table>", "<columns>", "<tab>"], 1),
        ],
    },
    "css": {
        "name": "CSS",
        "short": "CSS",
        "icon": "#",
        "color": "indigo",
        "description": "Style responsive interfaces with modern CSS.",
        "lessons": [
            ("Selectors and declarations", "CSS rules use selectors to choose elements and declarations to set their appearance. A declaration contains a property and value. Keep styles in a separate stylesheet and prefer reusable classes for repeated patterns.", ".notice {\n  color: #173a32;\n  background-color: #e9f4ed;\n  padding: 1rem;\n}"),
            ("The box model", "Every element has content, padding, border, and margin areas. The box-sizing property controls how width and height are calculated. border-box makes dimensions include padding and border, which is often easier to reason about.", "* { box-sizing: border-box; }\n.card {\n  width: 20rem;\n  padding: 1.25rem;\n  border: 1px solid #ddd;\n}"),
            ("Color and typography", "CSS controls color, font families, sizes, line height, and spacing. Use a readable line height and sufficient contrast. Relative units such as rem scale more comfortably with user preferences than fixed pixel-only typography.", "body {\n  color: #202a27;\n  font-family: system-ui, sans-serif;\n  font-size: 1rem;\n  line-height: 1.6;\n}"),
            ("Flexbox and grid", "Flexbox arranges items along one axis and is useful for navigation bars and aligned controls. Grid lays out rows and columns together, making it a strong choice for card collections and page layouts.", ".course-grid {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));\n  gap: 1rem;\n}"),
            ("Responsive design and states", "Media queries adapt presentation to viewport conditions. Start with a flexible layout, then add breakpoints only where the content needs them. Use :focus-visible styles so keyboard users can see which control is active.", "@media (max-width: 40rem) {\n  .toolbar { flex-direction: column; }\n}\nbutton:focus-visible { outline: 3px solid #e1a34b; }"),
        ],
        "practice": [
            "Style a student profile card using a class selector, readable text and background colors, padding, and a visible border. Keep the CSS in its own stylesheet.",
            "Create a course card and use border-box sizing to give it predictable dimensions. Add padding, a border, and outside spacing; compare the result with content-box sizing.",
            "Define a typography system for a lesson page with a readable body font, a clear heading scale, comfortable line-height, and colors with sufficient contrast.",
            "Build a responsive three-card course layout with CSS Grid. Make the columns shrink to one per row on a narrow screen and use consistent gaps.",
            "Add a small-screen media query that stacks the navigation and course cards. Give links and buttons a clear :focus-visible outline and verify it with the keyboard.",
        ],
        "quiz": [
            ("What does CSS control?", ["Web page presentation", "Database storage", "Network routing", "HTML content"], 0),
            ("Which symbol starts a class selector?", ["#", ".", "@", ":"], 1),
            ("Which property sets text color?", ["font-color", "text", "color", "foreground"], 2),
            ("What are the four main box model areas?", ["Content, padding, border, margin", "Text, image, link, form", "Width, height, top, left", "Row, column, grid, flex"], 0),
            ("Which display mode is designed for two-dimensional layouts?", ["inline", "grid", "float", "contents"], 1),
            ("Which property creates space inside an element's border?", ["margin", "gap", "padding", "outline"], 2),
            ("What does a media query help create?", ["Responsive styles", "HTML forms", "Database indexes", "Java methods"], 0),
            ("Which pseudo-class targets keyboard-visible focus?", [":hover", ":focus-visible", ":active-only", "::focus"], 1),
            ("What is the common role of Flexbox?", ["One-dimensional layout", "Image compression", "Form validation", "Color parsing"], 0),
            ("Which unit is relative to the root font size?", ["rem", "px", "cm", "pt"], 0),
        ],
    },
}

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "local-development-key-change-before-deploy")
app.config["DATABASE"] = str(DATABASE)


@app.template_filter("duration")
def format_duration(seconds):
    seconds = int(seconds or 0)
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes:02d}m"
    if minutes:
        return f"{minutes}m {seconds:02d}s"
    return f"{seconds}s"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(database=None):
    path = database or app.config["DATABASE"]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    try:
        db.execute("PRAGMA foreign_keys = ON")
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                register_number TEXT NOT NULL UNIQUE,
                screen_seconds INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS study_time (
                student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                language TEXT NOT NULL,
                seconds INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (student_id, language)
            );
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                language TEXT NOT NULL,
                score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 10),
                passed INTEGER NOT NULL CHECK (passed IN (0, 1)),
                created_at TEXT NOT NULL
            );
            """
        )
        db.commit()
    finally:
        db.close()


def current_student():
    student_id = session.get("student_id")
    if student_id is None:
        return None
    return get_db().execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()


def require_student():
    student = current_student()
    if student is None:
        return None
    return student


def course_progress(student_id):
    db = get_db()
    study = {
        row["language"]: row["seconds"]
        for row in db.execute("SELECT language, seconds FROM study_time WHERE student_id = ?", (student_id,))
    }
    best = {
        row["language"]: row["best_score"]
        for row in db.execute(
            "SELECT language, MAX(score) AS best_score FROM quiz_attempts WHERE student_id = ? GROUP BY language",
            (student_id,),
        )
    }
    passed = {
        row["language"]
        for row in db.execute(
            "SELECT DISTINCT language FROM quiz_attempts WHERE student_id = ? AND passed = 1",
            (student_id,),
        )
    }
    return study, best, passed


@app.route("/")
def welcome():
    if current_student():
        return redirect(url_for("dashboard"))
    return render_template("welcome.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_student():
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        register_number = request.form.get("register_number", "").strip()
        if not name or not register_number:
            flash("Please enter both your name and register number.", "error")
            return render_template("login.html"), 400
        if len(name) > 80 or len(register_number) > 40:
            flash("Name or register number is too long.", "error")
            return render_template("login.html"), 400
        db = get_db()
        db.execute(
            """INSERT INTO students (name, register_number, created_at) VALUES (?, ?, ?)
               ON CONFLICT(register_number) DO UPDATE SET name = excluded.name""",
            (name, register_number, datetime.now(timezone.utc).isoformat()),
        )
        student = db.execute(
            "SELECT id FROM students WHERE register_number = ?", (register_number,)
        ).fetchone()
        db.commit()
        session.clear()
        session["student_id"] = student["id"]
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("welcome"))


@app.route("/dashboard")
def dashboard():
    student = require_student()
    if student is None:
        return redirect(url_for("login"))
    study, best, passed = course_progress(student["id"])
    return render_template(
        "dashboard.html",
        student=student,
        courses=COURSES,
        study=study,
        best=best,
        passed=passed,
        minimum_study=300,
    )


@app.route("/materials/<language>")
def first_lesson(language):
    if language not in COURSES:
        abort(404)
    return redirect(url_for("lesson", language=language, page=1))


@app.route("/materials/<language>/<int:page>")
def lesson(language, page):
    student = require_student()
    if student is None:
        return redirect(url_for("login"))
    course = COURSES.get(language)
    if course is None:
        abort(404)
    if page < 1 or page > len(course["lessons"]):
        abort(404)
    study, best, passed = course_progress(student["id"])
    title, content, code = course["lessons"][page - 1]
    return render_template(
        "lesson.html",
        student=student,
        course=course,
        language=language,
        page=page,
        total_pages=len(course["lessons"]),
        title=title,
        content=content,
        code=code.strip(),
        practice=course["practice"][page - 1],
        study=study.get(language, 0),
        track_language=True,
        passed=language in passed,
        can_quiz=study.get(language, 0) >= 300,
    )


@app.route("/quiz/<language>")
def quiz(language):
    student = require_student()
    if student is None:
        return redirect(url_for("login"))
    course = COURSES.get(language)
    if course is None:
        abort(404)
    study, _best, _passed = course_progress(student["id"])
    if study.get(language, 0) < 300:
        flash("Study this course for at least 5 minutes to unlock its quiz.", "error")
        return redirect(url_for("lesson", language=language, page=1))
    result = None
    if session.get("quiz_result", {}).get("language") == language:
        result = session.pop("quiz_result")
    return render_template("quiz.html", student=student, course=course, language=language, result=result)


@app.route("/quiz/<language>/submit", methods=["POST"])
def submit_quiz(language):
    student = require_student()
    if student is None:
        return redirect(url_for("login"))
    course = COURSES.get(language)
    if course is None:
        abort(404)
    study, _best, _passed = course_progress(student["id"])
    if study.get(language, 0) < 300:
        flash("Study this course for at least 5 minutes to unlock its quiz.", "error")
        return redirect(url_for("lesson", language=language, page=1))
    score = sum(
        1 for index, question in enumerate(course["quiz"])
        if request.form.get(f"answer_{index}") == str(question[2])
    )
    passed = score >= 7
    get_db().execute(
        "INSERT INTO quiz_attempts (student_id, language, score, passed, created_at) VALUES (?, ?, ?, ?, ?)",
        (student["id"], language, score, int(passed), datetime.now(timezone.utc).isoformat()),
    )
    get_db().commit()
    session["quiz_result"] = {"language": language, "score": score, "passed": passed}
    return redirect(url_for("quiz", language=language))


@app.route("/report")
def report():
    student = require_student()
    if student is None:
        return redirect(url_for("login"))
    study, best, passed = course_progress(student["id"])
    attempts = get_db().execute(
        """SELECT language, score, passed, created_at FROM quiz_attempts
           WHERE student_id = ? ORDER BY created_at DESC""",
        (student["id"],),
    ).fetchall()
    return render_template(
        "report.html",
        student=student,
        courses=COURSES,
        study=study,
        best=best,
        passed=passed,
        attempts=attempts,
        overall=round(len(passed) / len(COURSES) * 100),
    )


@app.route("/api/time", methods=["POST"])
def record_time():
    student = require_student()
    if student is None:
        return jsonify(error="Please sign in again."), 401
    payload = request.get_json(silent=True) or {}
    seconds = payload.get("seconds")
    language = payload.get("language")
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not 0 <= seconds <= 45:
        return jsonify(error="Invalid time interval."), 400
    if language is not None and language not in COURSES:
        return jsonify(error="Unknown course."), 400
    seconds = int(seconds)
    db = get_db()
    db.execute("UPDATE students SET screen_seconds = screen_seconds + ? WHERE id = ?", (seconds, student["id"]))
    if language is not None and seconds:
        db.execute(
            """INSERT INTO study_time (student_id, language, seconds) VALUES (?, ?, ?)
               ON CONFLICT(student_id, language) DO UPDATE SET seconds = seconds + excluded.seconds""",
            (student["id"], language, seconds),
        )
    db.commit()
    total = db.execute("SELECT screen_seconds FROM students WHERE id = ?", (student["id"],)).fetchone()
    language_seconds = 0
    if language:
        row = db.execute(
            "SELECT seconds FROM study_time WHERE student_id = ? AND language = ?",
            (student["id"], language),
        ).fetchone()
        language_seconds = row["seconds"] if row else 0
    return jsonify(screen_seconds=total["screen_seconds"], language_seconds=language_seconds)


if __name__ == "__main__":
    init_db()
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
