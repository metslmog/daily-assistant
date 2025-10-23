import { useState, useEffect } from "react";

export default function Settings() {
  const [home, setHome] = useState("");
  const [work, setWork] = useState("");

  // Load saved values on mount
  useEffect(() => {
    const savedHome = localStorage.getItem("home");
    const savedWork = localStorage.getItem("work");
    if (savedHome) setHome(savedHome);
    if (savedWork) setWork(savedWork);
  }, []);

  // Save to localStorage whenever updated
  const handleSave = () => {
    localStorage.setItem("home", home);
    localStorage.setItem("work", work);
    alert("Saved!");
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-2xl">
      <h1 className="text-2xl font-bold mb-4">Settings</h1>

      <label className="block mb-2 font-medium">Home Address</label>
      <input
        type="text"
        value={home}
        onChange={(e) => setHome(e.target.value)}
        className="w-full border rounded-lg p-2 mb-4"
        placeholder="Enter your home address"
      />

      <label className="block mb-2 font-medium">Work Address</label>
      <input
        type="text"
        value={work}
        onChange={(e) => setWork(e.target.value)}
        className="w-full border rounded-lg p-2 mb-4"
        placeholder="Enter your work address"
      />

      <button
        onClick={handleSave}
        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
      >
        Save
      </button>
    </div>
  );
}
