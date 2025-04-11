document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.toggle').forEach(button => {
        button.addEventListener('click', () => {
            const taskId = button.dataset.id;
            fetch(`/toggle/${taskId}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        location.reload();
                    }
                });
        });
    });
});
