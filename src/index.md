---
toc: false
theme: [alt, light]
---

<!-- Load and transform the data -->

```js
// Load and process the data
const data = await FileAttachment("data/resto_data.json").json();
const {users, visits, restaurants, stats} = data;

// Process dates for daily metrics
function processDailyMetrics(users, visits) {
  const dateRange = d3.timeDays(
    new Date('2025-03-08'),
    new Date('2025-03-16')
  );
  
  // Count daily signups
  const signupsByDay = d3.rollup(
    users,
    v => v.length,
    d => d3.timeDay(new Date(d.created_at))
  );
  
  // Count daily check-ins
  const checkinsByDay = d3.rollup(
    visits,
    v => v.length,
    d => d3.timeDay(new Date(d.created_at))
  );


  
  return dateRange.map(date => ({
    date: d3.timeFormat("%Y-%m-%d")(date),
    signups: signupsByDay.get(date) || 0,
    checkins: checkinsByDay.get(date) || 0
  }));
}

// Calculate metrics
const dailyMetrics = processDailyMetrics(users, visits);
const totalSignups = users.length;
const totalCheckins = visits.length;
const visitedRestaurants = stats.visitedRestaurants;

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

// Create bins for the histogram using d3.bin
const binGenerator = d3.bin()
  .domain([0, 29])
  .thresholds(29); // Create 10 bins

const bins = binGenerator(visitsPerUserArray);
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
  <div class="card p-4">${
    resize((width) => Plot.plot({
      title: "Daily Sign-ups",
      width,
      height: 400,
      marginBottom: 30,
      x: {
        type: "band",
        label: "Date",
        tickFormat: d => d3.timeFormat("%b %d")(new Date(d))
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
        Plot.rectY(dailyMetrics.flatMap(d => [
          {date: d.date, value: d.signups, type: "Sign-ups"}
        ]), {
          x: "date",
          y: "value",
          fill: "type",
          title: d => `${d.type}: ${d.value}`
        })
      ]
    }))
  }</div>
  <div class="card p-4">${
    resize((width) => Plot.plot({
      title: "Daily Check-ins",
      width,
      height: 400,
      marginBottom: 30,
      x: {
        type: "band",
        label: "Date",
        tickFormat: d => d3.timeFormat("%b %d")(new Date(d))
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
          title: d => `${d3.timeFormat("%B %d")(new Date(d.date))}: ${d.checkins} check-ins`
        })
      ]
    }))
  }</div>
</div>

<div class="card p-4 mb-4">${
  resize((width) => Plot.plot({
    title: "Distribution of Visits per User",
    subtitle: `Average: ${avgVisits ? avgVisits.toFixed(1) : "0"} visits per user`,
    width,
    height: 300,
    marginBottom: 30,
    marks: [
      Plot.rectY(bins, {
        x1: d => d.x0,
        x2: d => d.x1,
        y: d => d.length,
        fill: "#8b5cf6",
        title: d => `${d.length} users with ${d.x0}-${d.x1} visits`
      }),
      Plot.ruleY([0])
    ],
    x: {
      label: "Number of Visits",
      domain: [0, 29]
    },
    y: {
      label: "Number of Users",
      grid: true
    }
  }))
}</div>

<link rel="stylesheet" href="styles/main.css">
