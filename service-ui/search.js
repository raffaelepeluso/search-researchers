document.addEventListener('DOMContentLoaded', function() {
    console.log("Document loaded");

    document.getElementById('searchButton').addEventListener('click', function() {
        console.log("Cerca button clicked");
        const name = document.getElementById('searchInput').value;
        if (name.trim() === "") {
            alert("Per favore, inserisci un nome.");
            return;
        }
        console.log("Fetching data for name:", name);

        fetch(`http://172.16.174.106:3001/researchers/info/${name}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        })
        .then(response => {
            console.log("Response received");
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log("Data received", data);
            const resultsTable = document.getElementById('resultsTable');
            const tbody = resultsTable.querySelector('tbody');
            tbody.innerHTML  = ''
            if(data.researchers){
                if(data.researchers.length > 1){
                    data.researchers.forEach(researcher => {

                        let escapedUniversity = researcher.university.replace(/'/g, ' ');
                        let escapedDepartment = researcher.department.replace(/'/g, ' ');
                        let escapedRole = researcher.role.replace(/'/g, ' ');
                        let escapedSsd = researcher.ssd.replace(/'/g, ' ');

                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${researcher.name}</td>
                            <td>${researcher.surname}</td>
                            <td>${researcher.university}</td>
                            <td>${researcher.department}</td>
                            <td>${researcher.role}</td>
                            <td>${researcher.ssd}</td>
                            <td><button onclick="viewDetails(${researcher.researcher_id}, '${researcher.name}', '${researcher.surname}', '${escapedUniversity}', '${escapedDepartment}', '${escapedRole}', '${escapedSsd}')">View Details</button></td>
                        `;
                        tbody.appendChild(row);
                    });
                    resultsTable.style.display = 'table';
                
                } else if(data.researchers.length == 1){
                    researcher = data.researchers[0];
                    let escapedUniversity = researcher.university.replace(/'/g, ' ');
                    let escapedDepartment = researcher.department.replace(/'/g, ' ');
                    let escapedRole = researcher.role.replace(/'/g, ' ');
                    let escapedSsd = researcher.ssd.replace(/'/g, ' ');
                    viewDetails(researcher.researcher_id, researcher.name, researcher.surname, escapedUniversity, escapedDepartment, escapedRole, escapedSsd);
                }

            } else {
                resultsTable.style.display = 'none';
                alert('Nessun ricercatore trovato.');
            }
        }
        )
        .catch(error => console.error('Error:', error));
    });
    
    window.viewDetails = function(researcherId, name, surname, university, department, role, ssd) {
        console.log("Viewing details for researcher ID:", researcherId);
        const params = new URLSearchParams({
            id: researcherId,
            name: name,
            surname: surname,
            university: university,
            department: department,
            role: role,
            ssd: ssd
        });
        window.location.href = `details.html?${params.toString()}`;
    }
});
