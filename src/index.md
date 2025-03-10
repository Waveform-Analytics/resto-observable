---
toc: false
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
```

# Pleasure Island Restaurant Week

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Total sign ups</h3>
    <div style="font-size: 2em; font-weight: bold;">${totalSignups}</div>

  </div>

  <div class="card">
    <h3>Total check ins</h3>
    <div style="font-size: 2em; font-weight: bold;">${totalCheckins}</div>
  </div>

  <div class="card">
    <h3>Number of restaurants visited</h3>
    <div style="font-size: 2em; font-weight: bold;">${visitedRestaurants}</div>
  </div>

</div>


<div class="grid grid-cols-2" style="grid-auto-rows: 504px;">
  <div class="card">${
    resize((width) => Plot.plot({
      title: "Daily check-ins",
      width,
      height: 300,
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
  <div class="card">${
    resize((width) => Plot.plot({
      title: "Daily Sign-ups",
      width,
      height: 300,
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
        domain: ["Check-ins", "Sign-ups"],
        range: [ "#10b981"]
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
</div>

<link rel="stylesheet" href="styles/main.css">
