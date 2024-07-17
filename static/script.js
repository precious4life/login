document.addEventListener('DOMContentLoaded', function() {
    let points = 0;
    const pointsButton = document.getElementById('points-button');
    pointsButton.textContent = `Points: ${points}`;

    document.querySelectorAll('.task-link').forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const taskId = this.getAttribute('data-task-id');
            fetch('/complete_task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ task_id: taskId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    points = data.points;
                    pointsButton.textContent = `Points: ${points}`;
                    alert(`Task ${taskId} completed! You earned points.`);
                } else {
                    alert('Failed to complete the task.');
                }
            });
        });
    });
});
