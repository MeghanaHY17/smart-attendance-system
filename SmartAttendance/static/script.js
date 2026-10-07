let registerStream = null;
let attendanceStream = null;


// --------------------------------
// Change sections
// --------------------------------

function showSection(sectionName) {

    const sections =
        document.querySelectorAll(".section");

    sections.forEach(section => {
        section.classList.remove("active");
    });

    document
        .getElementById(sectionName)
        .classList.add("active");

    if (sectionName === "records") {
        loadAttendance();
    }
}


// --------------------------------
// Register camera
// --------------------------------

async function startRegisterCamera() {

    try {

        registerStream =
            await navigator.mediaDevices.getUserMedia({
                video: true
            });

        document.getElementById(
            "registerVideo"
        ).srcObject = registerStream;

        document.getElementById(
            "registerMessage"
        ).innerText = "Camera started.";

    } catch (error) {

        document.getElementById(
            "registerMessage"
        ).innerText =
            "Camera permission denied.";
    }
}


// --------------------------------
// Capture student
// --------------------------------

async function captureStudent() {

    const studentId =
        document.getElementById(
            "studentId"
        ).value.trim();

    const studentName =
        document.getElementById(
            "studentName"
        ).value.trim();

    const video =
        document.getElementById(
            "registerVideo"
        );

    const canvas =
        document.getElementById(
            "registerCanvas"
        );

    const message =
        document.getElementById(
            "registerMessage"
        );


    if (!studentId || !studentName) {

        message.innerText =
            "Please enter Student ID and Name.";

        return;
    }


    if (!registerStream) {

        message.innerText =
            "Please open the camera first.";

        return;
    }


    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context =
        canvas.getContext("2d");

    context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );


    canvas.toBlob(async function(blob) {

        const formData = new FormData();

        formData.append(
            "student_id",
            studentId
        );

        formData.append(
            "name",
            studentName
        );

        formData.append(
            "image",
            blob,
            "face.jpg"
        );


        message.innerText =
            "Registering student...";


        try {

            const response =
                await fetch(
                    "/register",
                    {
                        method: "POST",
                        body: formData
                    }
                );

            const data =
                await response.json();

            message.innerText =
                data.message;

            if (data.success) {

                document.getElementById(
                    "studentId"
                ).value = "";

                document.getElementById(
                    "studentName"
                ).value = "";
            }

        } catch (error) {

            message.innerText =
                "Registration failed.";
        }

    }, "image/jpeg");
}


// --------------------------------
// Attendance camera
// --------------------------------

async function startAttendanceCamera() {

    try {

        attendanceStream =
            await navigator.mediaDevices.getUserMedia({
                video: true
            });

        document.getElementById(
            "attendanceVideo"
        ).srcObject =
            attendanceStream;

        document.getElementById(
            "attendanceMessage"
        ).innerText =
            "Camera started.";

    } catch (error) {

        document.getElementById(
            "attendanceMessage"
        ).innerText =
            "Camera permission denied.";
    }
}


// --------------------------------
// Recognize student
// --------------------------------

async function recognizeStudent() {

    const video =
        document.getElementById(
            "attendanceVideo"
        );

    const canvas =
        document.getElementById(
            "attendanceCanvas"
        );

    const message =
        document.getElementById(
            "attendanceMessage"
        );


    if (!attendanceStream) {

        message.innerText =
            "Please start the camera first.";

        return;
    }


    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context =
        canvas.getContext("2d");

    context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );


    canvas.toBlob(async function(blob) {

        const formData =
            new FormData();

        formData.append(
            "image",
            blob,
            "attendance.jpg"
        );


        message.innerText =
            "Recognizing face...";


        try {

            const response =
                await fetch(
                    "/recognize",
                    {
                        method: "POST",
                        body: formData
                    }
                );

            const data =
                await response.json();


            if (data.success &&
                data.recognized) {

                message.innerText =
                    "✓ " + data.message;

            } else {

                message.innerText =
                    "✗ " + data.message;
            }


        } catch (error) {

            message.innerText =
                "Recognition failed.";
        }

    }, "image/jpeg");
}


// --------------------------------
// Stop camera
// --------------------------------

function stopCamera() {

    if (registerStream) {

        registerStream
            .getTracks()
            .forEach(track => track.stop());

        registerStream = null;
    }


    if (attendanceStream) {

        attendanceStream
            .getTracks()
            .forEach(track => track.stop());

        attendanceStream = null;
    }


    document.getElementById(
        "registerMessage"
    ).innerText = "Camera stopped.";

    document.getElementById(
        "attendanceMessage"
    ).innerText = "Camera stopped.";
}


// --------------------------------
// Load attendance
// --------------------------------

async function loadAttendance() {

    const table =
        document.getElementById(
            "attendanceTable"
        );

    table.innerHTML =
        "<tr><td colspan='5'>Loading...</td></tr>";


    try {

        const response =
            await fetch("/attendance");

        const records =
            await response.json();


        table.innerHTML = "";


        if (records.length === 0) {

            table.innerHTML =
                "<tr>" +
                "<td colspan='5'>" +
                "No attendance records." +
                "</td>" +
                "</tr>";

            return;
        }


        records.forEach(record => {

            const row =
                document.createElement("tr");

            row.innerHTML = `
                <td>${record.student_id}</td>
                <td>${record.name}</td>
                <td>${record.date}</td>
                <td>${record.time}</td>
                <td>${record.status}</td>
            `;

            table.appendChild(row);
        });


    } catch (error) {

        table.innerHTML =
            "<tr>" +
            "<td colspan='5'>" +
            "Could not load attendance." +
            "</td>" +
            "</tr>";
    }
}