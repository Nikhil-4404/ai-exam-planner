import React, { useEffect, useState } from 'react';
import client from '../api/client';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Calendar, Rocket, CheckCircle, XCircle } from 'lucide-react'; // Example icons usage

const Dashboard = () => {
    const [subjects, setSubjects] = useState([]);
    const [loading, setLoading] = useState(true);
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

    return (
        <div className="container">
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
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
                    {/* Left Col: Subjects */}
                    <div className="subjects-section">
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                            <h3>Your Subjects</h3>
                            <button className="btn btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}>+ Add New</button>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {subjects.length === 0 ? (
                                <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                                    No subjects added yet. Start by adding one!
                                </div>
                            ) : (
                                subjects.map(sub => (
                                    <div key={sub.id} className="card">
                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <h4 style={{ margin: 0 }}>{sub.name}</h4>
                                            <span style={{ fontSize: '0.8rem', background: 'rgba(255,255,255,0.1)', padding: '2px 8px', borderRadius: '4px' }}>
                                                Difficulty: {sub.difficulty}/10
                                            </span>
                                        </div>
                                        <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                                            Exam: {sub.exam_date}
                                        </div>
                                        <div style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>
                                            {sub.topics.length} Topics
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Right Col: Actions / Stats */}
                    <div className="stats-section">
                        <div className="card">
                            <h3>🚀 Generator</h3>
                            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                                Ready to study? Generate your personalized daily plan.
                            </p>
                            <button className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
                                Generate Schedule
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
