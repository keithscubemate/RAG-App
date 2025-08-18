import React, { useState } from "react";
import "./App.css";

function Admin() {
  const [deleteInput, setDeleteInput] = useState("");
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteResponse, setDeleteResponse] = useState("");
  const [deleteError, setDeleteError] = useState("");

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState("");

  const handleDeleteInputChange = (event) => {
    setDeleteInput(event.target.value);
    setDeleteResponse("");
    setDeleteError("");
  };

  const handleDeleteSubmit = async (event) => {
    event.preventDefault();
    if (!deleteInput.trim()) {
      setDeleteError("Please enter a file name for deletion.");
      setDeleteResponse("");
      return;
    }

    setDeleteLoading(true);
    setDeleteResponse("");
    setDeleteError("");

    try {
      const response = await fetch("/api/filedeletion", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_message: deleteInput }),
      });

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({ detail: `HTTP error! Status: ${response.status}` }));
        throw new Error(
          errorData.detail || `HTTP error! Status: ${response.status}`,
        );
      }

      const data = await response.json();
      setDeleteResponse(data.message);
      setDeleteInput("");
    } catch (error) {
      console.error("File Deletion Error:", error);
      setDeleteError(`Deletion error: ${error.message}.`);
      setDeleteResponse("");
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setUploadMessage("");
    setUploadError("");
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setUploadError("Please select a file to upload.");
      setUploadMessage("");
      return;
    }

    setUploadLoading(true);
    setUploadMessage("");
    setUploadError("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("/api/rag", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({ detail: `HTTP error! Status: ${response.status}` }));
        throw new Error(
          errorData.detail || `HTTP error! Status: ${response.status}`,
        );
      }

      const data = await response.json();
      setUploadMessage(data.message);
      setSelectedFile(null);
      document.getElementById("file-upload-input").value = "";
    } catch (error) {
      console.error("File Upload Error:", error);
      setUploadError(`Upload error: ${error.message}.`);
      setUploadMessage("");
    } finally {
      setUploadLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Admin Interface</h1>
      <div className="section">
        <h2>Delete File by Name</h2>
        {deleteLoading && (
          <p className="loading-message">Processing deletion...</p>
        )}
        {deleteResponse && <p className="response-message">{deleteResponse}</p>}
        {deleteError && <p className="error-message">{deleteError}</p>}

        <form onSubmit={handleDeleteSubmit}>
          <input
            type="text"
            className = "delete-input"
            value={deleteInput}
            onChange={handleDeleteInputChange}
            placeholder="Type file name to delete"
            disabled={deleteLoading}
          />
          <button type="submit" className="delete-button" disabled={deleteLoading}>
            Delete File
          </button>
        </form>
      </div>

      <div className="section">
        <h2>Upload File</h2>
        {uploadLoading && <p className="loading-message">Uploading file...</p>}
        {uploadMessage && <p className="response-message">{uploadMessage}</p>}
        {uploadError && <p className="error-message">{uploadError}</p>}

        <input
          type="file"
          id="file-upload-input"
          onChange={handleFileChange}
          disabled={uploadLoading}
        />
        <button
          onClick={handleFileUpload}
          disabled={!selectedFile || uploadLoading}
        >
          Upload Selected File
        </button>
        {selectedFile && <p>Selected: {selectedFile.name}</p>}
      </div>
    </div>
  );
}

export default Admin;
