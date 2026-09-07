const API_URL = "http://localhost:5002";

async function findComplaint() {
    const id = document.getElementById("complaintId").value;

    if (!id) {
        document.getElementById("complaintDetails").innerHTML =
            "<p>Please enter a Complaint ID.</p>";
        return;
    }

    try {
        const response = await fetch(API_URL + "/complaints/" + id);
        const data = await response.json();

        if (response.ok) {
            document.getElementById("complaintDetails").innerHTML =
                `<h3>Complaint Details</h3>
                <p><strong>Complaint ID:</strong> ${data.complaint_id}</p>
                <p><strong>Citizen ID:</strong> ${data.citizen_id}</p>
                <p><strong>Issue:</strong> ${data.description}</p>
                <p><strong>Location:</strong> ${data.location}</p>
                <p><strong>Status:</strong> ${data.status}</p>`;
        } else {
            document.getElementById("complaintDetails").innerHTML =
                `<p>${data.error}</p>`;
        }

    } catch (error) {
        document.getElementById("complaintDetails").innerHTML =
            "<p>Complaint Service is unavailable.</p>";
    }
}
