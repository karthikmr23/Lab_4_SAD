const API_URL = "http://localhost:5002";

document.getElementById("complaintForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const citizenId =
            document.getElementById("citizenId").value;

        const complaintType =
            document.getElementById("complaintType").value;

        const description =
            document.getElementById("description").value;

        const location =
            document.getElementById("location").value;

        try {
            const response = await fetch(API_URL + "/complaints", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    citizen_id: citizenId,
                    complaint_type: complaintType,
                    description: description,
                    location: location
                })
            });

            const data = await response.json();

            if (response.ok) {
                document.getElementById("result").innerHTML =
                    `<h3>Complaint Registered</h3>
                    Complaint ID: ${data.complaint_id}<br>
                    Citizen: ${data.citizen_name}<br>
                    Type: ${data.complaint_type}<br>
                    Department: ${data.department}<br>
                    Officer: ${data.officer}<br>
                    Status: ${data.status}`;
            } else {
                document.getElementById("result").innerHTML =
                    `<p>${data.error}</p>`;
            }

        } catch (error) {
            document.getElementById("result").innerHTML =
                `<p>Complaint Service is unavailable.</p>`;
        }
    });


async function findComplaint() {

    const id =
        document.getElementById("searchComplaintId").value;

    if (!id) {
        document.getElementById("complaintDetails").innerHTML =
            "<p>Please enter a Complaint ID.</p>";
        return;
    }

    try {
        const response =
            await fetch(API_URL + "/complaints/" + id);

        const data = await response.json();

        if (response.ok) {
            document.getElementById("complaintDetails").innerHTML =
                `<h3>Complaint Details</h3>
                Complaint ID: ${data.complaint_id}<br>
                Citizen ID: ${data.citizen_id}<br>
                Type: ${data.complaint_type}<br>
                Issue: ${data.description}<br>
                Location: ${data.location}<br>
                Department: ${data.department}<br>
                Officer: ${data.officer}<br>
                Status: ${data.status}`;
        } else {
            document.getElementById("complaintDetails").innerHTML =
                `<p>${data.error}</p>`;
        }

    } catch (error) {
        document.getElementById("complaintDetails").innerHTML =
            "<p>Complaint Service is unavailable.</p>";
    }
}
