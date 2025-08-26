// Simplified dashboard.js for attendance registration
document.addEventListener('DOMContentLoaded', function() {
    // Form submission handling
    const attendanceForm = document.querySelector('.attendance-form');
    
    if (attendanceForm) {
        attendanceForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const studentId = this.querySelector('input[name="student_id"]').value;
            
            // Show success message
            showToast(`Attendance marked for ID: ${studentId}`);
            
            // Clear the input and focus
            this.reset();
            this.querySelector('input[name="student_id"]').focus();
        });
    }

    // Toast notification system
    function showToast(message, type = 'success') {
        // Remove existing toast if any
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            existingToast.remove();
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        // Remove the toast after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
});
