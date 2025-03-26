import React, { useState } from "react";
import axios from "axios";

function App() {
  const [jsonData, setJsonData] = useState(""); // Store JSON as text
  const [file2, setFile2] = useState(null);
  const [output, setOutput] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleJsonChange = (event) => {
    setJsonData(event.target.value);
    console.log(jsonData)
  };

  const handleFileChange = (event) => {
    setFile2(event.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!jsonData) {
      alert("Please enter JSON data.");
      return;
    }

    setLoading(true);
    try {
      // Ensure the input is valid JSON
      const parsedJson = JSON.parse(jsonData);
      console.log(parsedJson)
      // Send JSON request
      const response = await axios.post("http://localhost:8000/generate-rules", 
        { json_input: parsedJson }, 
        { headers: { "Content-Type": "application/json" } }
      );
  
      setOutput(response.data);
      if (file2) {
        const formData = new FormData();
        formData.append("file", file2);
        formData.append("rules", new Blob([JSON.stringify(response.data)], { type: "application/json" }));
        
        const fileResponse = await axios.post("http://localhost:8000/validate-dataset", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        
        setOutput((prevOutput) => ({
          ...prevOutput,
          fileValidation: fileResponse.data,
        }));
    }
    } catch (error) {
      console.error("Error processing request:", error.response?.data || error.message);
    }
    setLoading(false);
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Upload JSON & File for Processing</h1>
      
      {/* JSON Input */}
      <textarea
        value={jsonData}
        onChange={handleJsonChange}
        placeholder="Enter JSON data..."
        className="w-full p-2 border mb-2"
        rows="6"
      />

      {/* File Input */}
      <input type="file" onChange={handleFileChange} className="mb-4" />

      {/* Submit Button */}
      <button onClick={handleSubmit} className="bg-blue-500 text-white px-4 py-2 rounded">
        {loading ? "Processing..." : "Submit"}
      </button>

      {/* Output Display */}
      {output && (
        <div className="mt-4 p-4 border rounded bg-gray-100 shadow-md">
          <h2 className="text-lg font-semibold text-gray-700 mb-2">Output:</h2>
          <div className="bg-white p-2 border rounded overflow-auto max-h-64">
            <pre className="text-sm text-gray-900">{JSON.stringify(output, null, 2)}</pre>
          </div>
        </div>
      )}  
    </div>
  );
}

export default App;
