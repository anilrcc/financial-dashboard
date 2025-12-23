// Analyze industry trends from the heatmap data

const months = [
    "Nov 2024", "Dec 2024", "Jan 2025", "Feb 2025", "Mar 2025",
    "Apr 2025", "May 2025", "Jun 2025", "Jul 2025", "Aug 2025", "Sep 2025", "Oct 2025", "Nov 2025"
];

const data = {
    "Apparel, Leather & Allied Products": [0, 0, 0, 0, 0, 1, 0, 1, 1, 2, -10, -11, -11],
    "Chemical Products": [-9, -3, 4, 7, -3, 10, -2, -3, -8, -2, -6, -4, -5],
    "Computer & Electronic Products": [2, 0, -3, -2, 5, 6, 0, 6, -4, -3, -1, -1, 1],
    "Electrical Equipment, Appliances & Comp": [3, 2, 8, 6, 8, 4, 5, 9, -2, -4, -5, -5, 0],
    "Fabricated Metal Products": [-6, -6, -5, 9, 3, -1, 6, -1, -5, -1, 4, 5, -7],
    "Food, Beverage & Tobacco Products": [1, 0, -1, 5, -2, -3, -4, 8, -1, 4, 0, 2, 2],
    "Furniture & Related Products": [-5, 4, -4, -5, -4, -5, 4, 5, 6, -6, -7, -10, -3],
    "Machinery": [-4, -4, 5, -1, -1, 9, 7, 7, -7, -5, -2, -3, 4],
    "Miscellaneous Manufacturing": [-2, 6, -7, 2, 9, 8, 0, 4, 5, 6, 5, -2, 3],
    "Nonmetallic Mineral Products": [-3, -1, -8, -3, 6, 7, 2, 3, 3, 3, -3, 6, -4],
    "Paper Products": [-8, 5, -2, 0, -6, -4, -7, -4, -9, -10, -8, -9, -9],
    "Petroleum & Coal Products": [0, 0, 3, 1, 2, 2, 3, 2, 0, 5, 1, -6, -6],
    "Plastics & Rubber Products": [-10, 7, 7, 8, -5, 3, 1, 0, 2, -8, -9, 4, -1],
    "Primary Metals": [-1, 1, 2, 3, 4, 11, -1, 0, 7, 7, 2, 1, 0],
    "Printing & Related Support Activities": [-11, -5, 0, 0, 0, 0, -5, 0, -10, 0, 0, -8, 0],
    "Textile Mills": [0, -7, 1, -4, 1, 5, 0, -6, 4, 1, 3, -12, -8],
    "Transportation Equipment": [-7, -2, 6, 10, 7, -2, -3, -2, -3, -7, -4, 3, -2],
    "Wood Products": [0, 3, -6, 4, -7, -6, -6, -5, -6, -9, -11, -7, -10]
};

// Function to find consecutive growth/contraction periods
function findLongestPeriods(industryData) {
    let maxGrowth = 0;
    let maxContraction = 0;
    let currentGrowth = 0;
    let currentContraction = 0;

    for (let i = 0; i < industryData.length; i++) {
        if (industryData[i] > 0) {
            currentGrowth++;
            currentContraction = 0;
            maxGrowth = Math.max(maxGrowth, currentGrowth);
        } else if (industryData[i] < 0) {
            currentContraction++;
            currentGrowth = 0;
            maxContraction = Math.max(maxContraction, currentContraction);
        } else {
            currentGrowth = 0;
            currentContraction = 0;
        }
    }

    return { maxGrowth, maxContraction };
}

// Analyze all industries
const analysis = {};
for (const [industry, values] of Object.entries(data)) {
    const periods = findLongestPeriods(values);
    const latestValue = values[values.length - 1];
    const previousValue = values[values.length - 2];
    
    analysis[industry] = {
        ...periods,
        latestValue,
        previousValue,
        transition: getTransition(previousValue, latestValue)
    };
}

function getTransition(prev, curr) {
    if (prev < 0 && curr > 0) return 'contraction-to-growth';
    if (prev > 0 && curr < 0) return 'growth-to-contraction';
    if (prev === 0 && curr > 0) return 'stable-to-growth';
    if (prev === 0 && curr < 0) return 'stable-to-contraction';
    if (prev < 0 && curr === 0) return 'contraction-to-stable';
    if (prev > 0 && curr === 0) return 'growth-to-stable';
    return 'no-change';
}

// Sort by longest growth periods
const longestGrowth = Object.entries(analysis)
    .sort((a, b) => b[1].maxGrowth - a[1].maxGrowth)
    .slice(0, 3);

// Sort by longest contraction periods
const longestContraction = Object.entries(analysis)
    .sort((a, b) => b[1].maxContraction - a[1].maxContraction)
    .slice(0, 3);

// Find transitions
const contractionToGrowth = Object.entries(analysis)
    .filter(([_, data]) => data.transition === 'contraction-to-growth')
    .map(([industry, _]) => industry);

const growthToContraction = Object.entries(analysis)
    .filter(([_, data]) => data.transition === 'growth-to-contraction')
    .map(([industry, _]) => industry);

console.log('=== TOP 3 INDUSTRIES WITH LONGEST GROWTH PERIODS ===');
longestGrowth.forEach(([industry, data]) => {
    console.log(`${industry}: ${data.maxGrowth} months`);
});

console.log('\n=== TOP 3 INDUSTRIES WITH LONGEST CONTRACTION PERIODS ===');
longestContraction.forEach(([industry, data]) => {
    console.log(`${industry}: ${data.maxContraction} months`);
});

console.log('\n=== INDUSTRIES MOVING FROM CONTRACTION TO GROWTH (Latest Report) ===');
console.log(contractionToGrowth.length > 0 ? contractionToGrowth.join(', ') : 'None');

console.log('\n=== INDUSTRIES MOVING FROM GROWTH TO CONTRACTION (Latest Report) ===');
console.log(growthToContraction.length > 0 ? growthToContraction.join(', ') : 'None');

// Export for use in HTML
const insights = {
    longestGrowth: longestGrowth.map(([industry, data]) => ({ industry, months: data.maxGrowth })),
    longestContraction: longestContraction.map(([industry, data]) => ({ industry, months: data.maxContraction })),
    contractionToGrowth,
    growthToContraction
};

console.log('\n=== JSON OUTPUT ===');
console.log(JSON.stringify(insights, null, 2));
