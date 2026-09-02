const API_URL = "http://localhost:5003";

document.getElementById("departmentForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const departmentName =
            document.getElementById("departmentName").value;

        const officerName =
            document.getElementById("officerName").value;

        const ward =
            document.getElementById("ward").value;

        const contact =
            document.getElementById("contact").value;

        const response = await fetch(API_URL + "/departments", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                department_name: departmentName,
                officer_name: officerName,
                ward: ward,
                contact: contact
            })
        });

        const data = await response.json();

        document.getElementById("result").innerHTML =
            `<h3>Department Added</h3>
            Department ID: ${data.department_id}<br>
            Department: ${data.department_name}<br>
            Officer: ${data.officer_name}<br>
            Ward: ${data.ward}<br>
            Contact: ${data.contact}`;
    });

async function findDepartment() {

    const id =
        document.getElementById("searchDepartmentId").value;

    const response =
        await fetch(API_URL + "/departments/" + id);

    const data = await response.json();

    if (response.ok) {

        document.getElementById("departmentDetails").innerHTML =
            `<h3>Department Details</h3>
            ID: ${data.department_id}<br>
            Department: ${data.department_name}<br>
            Officer: ${data.officer_name}<br>
            Ward: ${data.ward}<br>
            Contact: ${data.contact}`;

    } else {

        document.getElementById("departmentDetails").innerHTML =
            data.error;
    }
}
