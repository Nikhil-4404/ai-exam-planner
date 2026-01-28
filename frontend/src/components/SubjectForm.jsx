import React, { useState, useEffect } from 'react';
import { Calendar, Save, Trash2, BookOpen, UploadCloud } from 'lucide-react';
import client from '../api/client';

const SubjectForm = ({ onAdd, initialData = null, onCancel }) => {
    const [name, setName] = useState('');
    const [date, setDate] = useState('');
    const [difficulty, setDifficulty] = useState(5);
    const [topics, setTopics] = useState('');
    const [isUploading, setIsUploading] = useState(false);

    useEffect(() => {
        if (initialData) {
            setName(initialData.name);
            setDate(initialData.exam_date);
            setDifficulty(initialData.difficulty);
            // Convert topics array to comma-separated string
            const topicString = initialData.topics.map(t => t.name).join(', ');
            setTopics(topicString);
        }
    }, [initialData]);

    const handlePdfUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await client.post('/syllabus/parse', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            if (res.data.success) {
                const newText = res.data.extracted_text;
                setTopics(prev => prev ? prev + ", " + newText : newText);
            } else {
                alert("Parsing Error: " + res.data.message);
            }
        } catch (err) {
            alert("Upload Failed: " + err.message);
        } finally {
            setIsUploading(false);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onAdd({ name, date, difficulty, topics });

        // Only clear if adding new, otherwise we might be editing
        if (!initialData) {
            setName('');
            setDate('');
            setDifficulty(5);
            setTopics('');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="card" style={{ border: initialData ? '1px solid #f59e0b' : '' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0 }}>
                    {initialData ? '✏️ Edit Subject' : '➕ Add New Subject'}
                </h3>
                {onCancel && (
                    <button type="button" className="btn btn-ghost" onClick={onCancel}>
                        Cancel
                    </button>
                )}
            </div>

            <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Subject Name</label>
                <input type="text" value={name} onChange={e => setName(e.target.value)} required placeholder="e.g. Physics" />
            </div>

            <div className="grid-cols-2">
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Exam Date</label>
                    <input type="date" value={date} onChange={e => setDate(e.target.value)} required />
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Difficulty (1-10)</label>
                    <input type="number" min="1" max="10" value={difficulty} onChange={e => setDifficulty(e.target.value)} />
                </div>
            </div>

            <div style={{ marginBottom: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    📄 AI Syllabus Parser
                </label>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <label className="btn btn-ghost" style={{ border: '1px dashed #4f46e5', cursor: 'pointer', flex: 1 }}>
                        <input type="file" accept=".pdf" onChange={handlePdfUpload} style={{ display: 'none' }} />
                        <UploadCloud size={16} style={{ marginRight: '8px' }} />
                        {isUploading ? 'Parsing...' : 'Upload PDF'}
                    </label>
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    Upload a syllabus PDF to automatically extract topics.
                </div>
            </div>

            <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Topics (Comma separated)</label>
                <textarea
                    value={topics}
                    onChange={e => setTopics(e.target.value)}
                    placeholder="e.g. Thermodynamics, Kinematics, Optics"
                    rows="4"
                ></textarea>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
                <Save size={18} style={{ marginRight: '8px' }} /> {initialData ? 'Update Subject' : 'Save Subject'}
            </button>
        </form>
    );
};

export default SubjectForm;
