// Weekly calendar grid layout JavaScript

async function loadWeeklyCalendar() {
    try {
        const startDate = currentWeekStart.toISOString().split('T')[0];
        const data = await API.getWeeklyCalendar(`?start_date=${startDate}`);

        // Calculate week range
        const weekEnd = new Date(currentWeekStart);
        weekEnd.setDate(weekEnd.getDate() + 6);
        const dateOptions = { month: 'short', day: 'numeric', year: 'numeric' };
        document.getElementById('week-range').textContent =
            `${currentWeekStart.toLocaleDateString('en-US', dateOptions)} - ${weekEnd.toLocaleDateString('en-US', dateOptions)}`;

        const eventsDiv = document.getElementById('weekly-events');

        // Create day columns for the week (Monday - Sunday)
        const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        const eventsByDay = {};

        // Initialize empty arrays for each day
        days.forEach(day => eventsByDay[day] = []);

        // Group events by day
        if (data.events && data.events.length > 0) {
            data.events.forEach(event => {
                const eventDate = new Date(event.date);
                const dayName = eventDate.toLocaleDateString('en-US', { weekday: 'long' });
                if (eventsByDay[dayName]) {
                    eventsByDay[dayName].push(event);
                }
            });
        }

        // Build grid HTML
        let gridHTML = '<div class="calendar-grid">';

        days.forEach((day, index) => {
            const dayDate = new Date(currentWeekStart);
            // Sunday is 0, Monday is 1, etc. Adjust index for Monday-first week
            dayDate.setDate(dayDate.getDate() + (index + 1) % 7);

            const dayEvents = eventsByDay[day] || [];

            gridHTML += `
                <div class="day-column">
                    <div class="day-header">
                        <div class="day-name">${day}</div>
                        <div class="day-date">${dayDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</div>
                    </div>
                    <div class="day-events">
            `;

            if (dayEvents.length === 0) {
                gridHTML += '<div class="no-events">No events</div>';
            } else {
                dayEvents.forEach(event => {
                    const eventDate = new Date(event.date);
                    const urgencyClass = event.urgency_level === 'urgent' ? 'urgent' :
                        event.urgency_level === 'high' ? 'high-priority' : 'normal';
                    const typeClass = `event-type-${event.event_type}`;
                    const typeLabel = event.event_type.charAt(0).toUpperCase() + event.event_type.slice(1);

                    gridHTML += `
                        <div class="event-item ${urgencyClass}" onclick="window.location.href='case-details.html?id=${event.case_id}'">
                            <div class="event-time">
                                ${eventDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                            </div>
                            <div class="event-desc">
                                <strong>${event.description || 'No description'}</strong>
                            </div>
                            <div>
                                <span class="event-type-badge ${typeClass}">${typeLabel}</span>
                            </div>
                            <div style="margin-top: 5px; font-size: 11px; color: #888;">
                                ${event.case_id}
                            </div>
                        </div>
                    `;
                });
            }

            gridHTML += `
                    </div>
                </div>
            `;
        });

        gridHTML += '</div>';
        eventsDiv.innerHTML = gridHTML;

    } catch (error) {
        console.error('Error loading calendar:', error);
        document.getElementById('weekly-events').innerHTML = '<p class="text-muted">Error loading events</p>';
    }
}
