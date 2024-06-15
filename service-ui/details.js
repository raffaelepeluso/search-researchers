const urlParams = new URLSearchParams(window.location.search);
const researcherId = urlParams.get('id');



console.log("Fetching details for researcher ID:", researcherId);

fetch(`http://172.16.174.106:3001/researchers/details/${researcherId}`)
    .then(response => response.json())
    .then(data => {
        console.log("Details received", data);
        document.getElementById('name').textContent = urlParams.get('name');
        document.getElementById('surname').textContent = urlParams.get('surname');
        document.getElementById('university').textContent = urlParams.get('university');
        document.getElementById('department').textContent = urlParams.get('department');
        document.getElementById('role').textContent = urlParams.get('role');
        document.getElementById('ssd').textContent = urlParams.get('ssd');
        document.getElementById('h_index').textContent = data.h_index;
        document.getElementById('n_citations').textContent = data.n_citations;
        document.getElementById('n_publications').textContent = data.n_publications;
        document.getElementById('topics_of_interest').textContent = data.topics_of_interest;

        // Fetch publications
        fetch(`http://172.16.174.106:3002/publications/${researcherId}`)
            .then(response => response.json())
            .then(publications => {
                console.log("Publications received", publications);
                const publicationsContainer = document.getElementById('publicationsContainer');
                publications.forEach(pub => {
                    const pubElement = document.createElement('div');
                    pubElement.innerHTML = `
                        <p><a href="${pub.link}" target="_blank">${pub.title}</a></p>
                        <p>Year: ${pub.year}</p>
                        <p>Authors: ${pub.authors}</p>
                        <p>Type: ${pub.type}</p>
                        <p>Num Citations: ${pub.num_citations}</p>
                        <p>Reference: ${pub.reference}</p>
                    `;
                    publicationsContainer.appendChild(pubElement);
                });
            })
            .catch(error => console.error('Error fetching publications:', error));
    })
    .catch(error => console.error('Error fetching details:', error));
