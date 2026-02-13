import React, { useMemo } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';

const COLORS = ['#00C49F', '#FFBB28', '#FF8042', '#0088FE'];

const AnalysisCharts = ({ subjects }) => {

    const chartData = useMemo(() => {
        if (!subjects || subjects.length === 0) return [];

        // 1. Subject Load (Stacked Bar)
        const subjectLoad = subjects.map(sub => {
            const completed = sub.topics.filter(t => t.status).length;
            const pending = sub.topics.length - completed;
            return {
                name: sub.name,
                completed,
                pending,
                total: sub.topics.length
            };
        });

        // 2. Difficulty Distribution (Pie)
        let easy = 0, medium = 0, hard = 0;
        subjects.forEach(sub => {
            if (sub.difficulty <= 4) easy++;
            else if (sub.difficulty <= 7) medium++;
            else hard++;
        });
        const difficultyDist = [
            { name: 'Easy (1-4)', value: easy, color: '#4ade80' },     // Green
            { name: 'Medium (5-7)', value: medium, color: '#facc15' }, // Yellow
            { name: 'Hard (8-10)', value: hard, color: '#f87171' }     // Red
        ].filter(d => d.value > 0);

        return { subjectLoad, difficultyDist };
    }, [subjects]);

    if (!subjects || subjects.length === 0) return null;

    return (
        <div className="animate-enter delay-200" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '2.5rem' }}>

            {/* Chart 1: Topic Progress per Subject */}
            <div className="card" style={{ height: '350px', display: 'flex', flexDirection: 'column' }}>
                <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', textAlign: 'center' }}>📊 Progress per Subject</h3>
                <div style={{ flex: 1, width: '100%', minHeight: 0 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartData.subjectLoad} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                            <XAxis dataKey="name" stroke="#cbd5e1" fontSize={12} tickLine={false} />
                            <YAxis stroke="#cbd5e1" fontSize={12} tickLine={false} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }}
                                itemStyle={{ color: '#fff' }}
                            />
                            <Legend wrapperStyle={{ paddingTop: '10px' }} />
                            <Bar dataKey="completed" name="Done" stackId="a" fill="#34d399" radius={[0, 0, 4, 4]} />
                            <Bar dataKey="pending" name="To Do" stackId="a" fill="#fbbf24" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Chart 2: Difficulty Distribution */}
            <div className="card" style={{ height: '350px', display: 'flex', flexDirection: 'column' }}>
                <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', textAlign: 'center' }}>⚡ Difficulty Breakdown</h3>
                <div style={{ flex: 1, width: '100%', minHeight: 0 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={chartData.difficultyDist}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {chartData.difficultyDist.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }}
                            />
                            <Legend verticalAlign="bottom" height={36} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default AnalysisCharts;
