import React, { useEffect, useState } from 'react';
import client from '../api/client';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Calendar, Rocket, CheckCircle, XCircle } from 'lucide-react';
import SubjectForm from '../components/SubjectForm';

const Dashboard = () => {
    const [subjects, setSubjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);
    const [schedule, setSchedule] = useState(null);
    const [dailyHours, setDailyHours] = useState(4);

    const navigate = useNavigate();
    const userId = localStorage.getItem('user_id');

    useEffect(() => {
        if (!userId) {
            navigate('/');
            return;
        }
        fetchSubjects();
    }, [userId]);

    const fetchSubjects = async () => {
        try {
            const res = await client.get(`/users/${userId}/subjects/`);
            setSubjects(res.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const handleAddSubject = async (formData) => {
        // Transform data for API
        const topicList = formData.topics.split(',').map(t => ({
            name: t.trim(),
            weightage: 1.0,
            status: false
        })).filter(t => t.name);

        const payload = {
            name: formData.name,
            exam_date: formData.date,
            difficulty: parseInt(formData.difficulty),
            topics: topicList
        };

        try {
            await client.post(`/users/${userId}/subjects/`, payload);
            fetchSubjects(); // Refresh list
            setShowAddForm(false);
        } catch (err) {
            alert("Failed to add subject: " + err.message);
        }
    };

    const handleGenerateSchedule = async () => {
        try {
            const res = await client.post(`/schedule/${userId}`, { daily_hours: dailyHours });
            setSchedule(res.data);
        } catch (err) {
            alert("Planning failed: " + err.message);
        }
    };

    return (
        <div className="container animate-enter">
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
                <div>
                    <h1>🎓 SmartStudy Dashboard</h1>
                    <p style={{ color: 'var(--text-muted)' }}>Welcome back, Student</p>
                </div>
                <button className="btn btn-ghost" onClick={() => { localStorage.removeItem('user_id'); navigate('/'); }}>
                    Log Out
                </button>
            </header>

            {loading ? (
                <div>Loading...</div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) minmax(0, 1fr)', gap: '2rem' }}>
                    {/* Left Col: Subjects */}
                    <div className="subjects-section">
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', alignItems: 'center' }}>
                            <h3>Your Subjects</h3>
                            <button
                                className="btn btn-primary"
                                style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                                onClick={() => setShowAddForm(!showAddForm)}
                            >
                                {showAddForm ? 'Cancel' : '+ Add New'}
                            </button>
                        </div>

                        {showAddForm && (
                            <div style={{ marginBottom: '2rem' }}>
                                <SubjectForm onAdd={handleAddSubject} />
                            </div>
                        )}

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {subjects.length === 0 ? (
                                <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                                    No subjects added yet. Start by adding one!
                                </div>
                            ) : (
                                subjects.map(sub => (
                                    <div key={sub.id} className="card">
                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <h4 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                <BookOpen size={16} /> {sub.name}
                                            </h4>
                                            <span style={{ fontSize: '0.8rem', background: 'rgba(255,255,255,0.1)', padding: '2px 8px', borderRadius: '4px' }}>
                                                Difficulty: {sub.difficulty}/10
                                            </span>
                                        </div>
                                        <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: 'var(--text-muted)', display: 'flex', gap: '1rem' }}>
                                            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                <Calendar size={14} /> {sub.exam_date}
                                            </span>
                                            <span>{sub.topics.length} Topics</span>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Right Col: Actions / Stats */}
                    <div className="stats-section">
                        <div className="card" style={{ position: 'sticky', top: '2rem' }}>
                            <h3>🚀 Generator</h3>
                            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                                Create your personalized daily plan based on urgency.
                            </p>

                            <label style={{ fontSize: '0.9rem', display: 'block', marginBottom: '0.5rem' }}>Daily Study Hours</label>
                            <input
                                type="number"
                                value={dailyHours}
                                onChange={e => setDailyHours(parseFloat(e.target.value))}
                                step="0.5"
                                min="0.5"
                                max="12"
                            />

                            <button onClick={handleGenerateSchedule} className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }}>
                                <Rocket size={18} style={{ marginRight: '8px' }} /> Generate Schedule
                            </button>

                            {schedule && (
                                <div style={{ marginTop: '2rem', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1rem' }}>
                                    <h4>Today's Plan</h4>
                                    {schedule.length === 0 ? (
                                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No pending tasks!</p>
                                    ) : (
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                            {schedule.map((item, idx) => (
                                                <div key={idx} style={{
                                                    background: 'rgba(0,0,0,0.2)',
                                                    padding: '0.75rem',
                                                    borderRadius: '8px',
                                                    borderLeft: `4px solid ${item.urgency_score > 1.5 ? '#ef4444' : '#fbbf24'}`
                                                }}>
                                                    <div style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{item.subject}</div>
                                                    <div style={{ fontSize: '0.85rem' }}>{item.topic}</div>
                                                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                                                        ⏱ {item.allocated_hours} hrs
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
