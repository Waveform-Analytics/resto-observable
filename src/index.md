---
toc: false
theme: [alt, light]
---

<!-- Load and transform the data -->

```js
// Load and process the data
const data = await FileAttachment("data/resto_data.json").json();
const {users, visits, restaurants, complete_counts, actual_counts, stats} = data;

// Process dates for daily metrics
function processDailyMetrics(users, visits) {
  // Create date range - explicitly set to midnight UTC
  const startDate = new Date('2025-03-08T00:00:00Z');
  const endDate = new Date('2025-03-16T00:00:00Z');
  const dateRange = d3.timeDays(startDate, endDate);
  
  // Count daily signups using UTC dates
  const signupsByDay = d3.rollup(
    users,
    v => v.length,
    d => {
      const date = new Date(d.created_at);
      return d3.utcFormat("%Y-%m-%d")(date);  // Use UTC format here
    }
  );
  
  // Count daily check-ins using UTC dates
  const checkinsByDay = d3.rollup(
    visits,
    v => v.length,
    d => {
      const date = new Date(d.created_at);
      return d3.utcFormat("%Y-%m-%d")(date);  // Use UTC format here
    }
  );



  const metrics = dateRange.map(date => {
    const dateStr = d3.utcFormat("%Y-%m-%d")(date);  // Use UTC format here
    return {
      date: dateStr,
      signups: signupsByDay.get(dateStr) || 0,
      checkins: checkinsByDay.get(dateStr) || 0
    };
  });


  return metrics;
}

// Calculate metrics
const dailyMetrics = processDailyMetrics(users, visits);
const totalSignups = users.length;
const totalCheckins = visits.length;
const visitedRestaurants = stats.visitedRestaurants;

// display(complete_counts);

// Calculate visits per user
const visitsPerUser = d3.rollup(
  visits,
  v => v.length,
  d => d.user_id
);

// Convert to array for histogram
const visitsPerUserArray = Array.from(visitsPerUser.values());

// Calculate some statistics
const maxVisits = d3.max(visitsPerUserArray) || 0;
const avgVisits = d3.mean(visitsPerUserArray) || 0;

// Create discrete distribution data with all possible visit counts
const visitDistribution = Array.from(
  { length: 29 }, // 1 to 29 visits
  (_, i) => ({
    visits: i + 1, // Start from 1 instead of 0
    count: Array.from(visitsPerUser.values()).filter(v => v === (i + 1)).length
  })
);

```

# Pleasure Island Restaurant Week

<div class="grid grid-cols-3 gap-4 mb-4">
  <div class="card p-4">
    <h3>Total sign ups</h3>
    <div style="font-size: 2em; font-weight: bold; color: #10b981;">${totalSignups}</div>
  </div>

  <div class="card p-4">
    <h3>Total check ins</h3>
    <div style="font-size: 2em; font-weight: bold; color: #3b82f6;">${totalCheckins}</div>
  </div>

  <div class="card p-4">
    <h3>Number of restaurants visited</h3>
    <div style="font-size: 2em; font-weight: bold;">${visitedRestaurants}</div>
  </div>
</div>

<div class="grid grid-cols-2 gap-4 mb-4">
  <div class="card p-4">
    <div class="mb-6">${
      resize((width) => Plot.plot({
        title: "Daily Sign-ups",
        width,
        height: 200,
        marginBottom: 30,
        x: {
          type: "band",
          label: "Date",
          tickFormat: d => {
            // Ensure we parse the date string and format it in UTC
            const date = new Date(d + 'T00:00:00Z');
            return d3.utcFormat("%a")(date);
          }
        },
        y: {
          label: "Count",
          grid: true
        },
        color: {
          domain: ["Sign-ups"],
          range: ["#10b981"]
        },
        marks: [
          Plot.rectY(dailyMetrics, {
            x: "date",
            y: "signups",
            fill: "#10b981",
            title: d => {
              const date = new Date(d.date + 'T00:00:00Z');
              return `${d3.utcFormat("%A")(date)}: ${d.signups} sign-ups`;
            }
          })
        ]
      }))
    }</div>
    <div>${
      resize((width) => Plot.plot({
        title: "Daily Check-ins",
        width,
        height: 200,
        marginBottom: 30,
        x: {
          type: "band",
          label: "Date",
          tickFormat: d => {
            const date = new Date(d + 'T00:00:00Z');
            return d3.utcFormat("%a")(date);
          }
        },
        y: {
          label: "Number of Check-ins",
          grid: true
        },
        marks: [
          Plot.rectY(dailyMetrics, {
            x: "date",
            y: "checkins",
            fill: "#3b82f6",
            title: d => {
              const date = new Date(d.date + 'T00:00:00Z');
              return `${d3.utcFormat("%A")(date)}: ${d.checkins} check-ins`;
            }
          })
        ]
      }))
    }</div>
  </div>
  <div class="card p-4">
    <!-- Cell Plot -->
      ${resize((width) => Plot.plot({
    title: "Visits by Hour and Day",
    width,
    height: 400,
    marginLeft: 60,
    marginBottom: 30,
    grid: true,
    x: {
      type: "band",
      label: "Hour",
      domain: d3.range(24),
      tickFormat: d => d,
      tickRotate: 0
    },
    y: {
      type: "band",
      label: null,
      domain: d3.range(8, 16),
      tickFormat: d => `Mar ${d}`
    },
    color: {
      type: "linear",
      scheme: "purples",
      domain: [0, 10],  // Compress the scale to make lower values more visible
      legend: true
    },
    marks: [
      Plot.cell(actual_counts, {
        x: "hour_of_day",
        y: "day_of_month",
        fill: "visit_count",
        title: d => `${d.visit_count} visits on March ${d.day_of_month} at ${d.hour_of_day.toString().padStart(2, '0')}:00`
      })
    ]
  }))}
  </div>
</div>

  

<div class="card p-4 mb-4">${
  resize((width) => Plot.plot({
    title: "Distribution of Visits per User",
    subtitle: `Average: ${avgVisits ? avgVisits.toFixed(1) : "0"} visits per user`,
    width,
    height: 300,
    marginBottom: 30,
    marks: [
      Plot.rectY(visitDistribution, {
        x: "visits",
        y: "count",
        fill: "#8b5cf6",
        title: d => `${d.count} user${d.count === 1 ? '' : 's'} with ${d.visits} visit${d.visits === 1 ? '' : 's'}`
      }),
      Plot.ruleY([0])
    ],
    x: {
      type: "band",
      label: "Number of Visits",
      domain: visitDistribution.map(d => d.visits)  // Explicitly set all possible values
    },
    y: {
      label: "Number of Users",
      grid: true
    }
  }))
}</div>

<link rel="stylesheet" href="styles/main.css">
