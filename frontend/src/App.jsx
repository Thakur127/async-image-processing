import { useState } from "react";
import axios from "axios";

const App = () => {
  const [files, setFiles] = useState();
  const [requestId, setRequestId] = useState("");
  const [queryRequestId, setQueryRequestId] = useState("");
  const [state, setState] = useState({ status: "", request_id: "" });

  const uploadFile = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("file", files[0]);
    setState({ status: "processing", request_id: "" });
    try {
      const { data } = await axios.post(
        "http://localhost:8000/api/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setRequestId(data?.requestId);
    } catch (error) {
      console.log(error);
    }
  };

  const checkStatus = async (e) => {
    setState({ status: "processing", request_id: queryRequestId });
    e.preventDefault();
    try {
      const { data } = await axios.get(
        "http://localhost:8000/api/status?request_id=" + queryRequestId
      );
      setState(data);
      setQueryRequestId("");
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="h-svh flex flex-col">
      <header className="bg-gray-200 shadow-md border-b p-4">
        <nav>
          <span>Assignment</span>
        </nav>
      </header>
      <main className="relative flex-col lg:flex-row flex gap-8 items-center lg:items-start">
        <form className="m-12 space-y-2" onSubmit={uploadFile}>
          <div className="max-w-60">
            {requestId && (
              <p>
                Your generated request Id is: <strong>{requestId}</strong>. Use
                this to check status of the request{" "}
              </p>
            )}
          </div>
          <div className="border rounded-md flex w-60 text-center">
            <label
              htmlFor="file"
              className="w-full h-full p-8 rounded-md cursor-pointer bg-gray-100 hover:bg-gray-200 transition-all"
            >
              {files?.[0]?.name || "Upload CSV file"}
            </label>
            <input
              type="file"
              id="file"
              required
              className="hidden"
              onChange={(e) => setFiles(e.target.files)}
            />
          </div>
          <button
            type="submit"
            className="border rounded-full py-3 px-8 bg-cyan-500 text-gray-100"
          >
            Upload
          </button>
        </form>
        <div className="mt-12 max-w-96">
          <form className="space-y-2" onSubmit={checkStatus}>
            <div className="space-y-2">
              <label>Check status for request id</label>
              <input
                type="text"
                value={queryRequestId}
                onChange={(e) => setQueryRequestId(e.target.value)}
                className="border rounded-full py-3 px-4 w-full outline-none"
                required
                placeholder="request id"
              />
            </div>
            <button
              type="submit"
              className="border rounded-full py-3 px-8 bg-cyan-500 text-gray-100"
            >
              Check Status
            </button>
          </form>
          <span>
            {state.status === "processing" ? (
              <p className="flex items-center">
                <span className="animate-spin">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 512 512"
                    className="w-4 h-4"
                  >
                    <path d="M222.7 32.1c5 16.9-4.6 34.8-21.5 39.8C121.8 95.6 64 169.1 64 256c0 106 86 192 192 192s192-86 192-192c0-86.9-57.8-160.4-137.1-184.1c-16.9-5-26.6-22.9-21.5-39.8s22.9-26.6 39.8-21.5C434.9 42.1 512 140 512 256c0 141.4-114.6 256-256 256S0 397.4 0 256C0 140 77.1 42.1 182.9 10.6c16.9-5 34.8 4.6 39.8 21.5z" />
                  </svg>
                </span>
                <span className="ml-2">
                  We are processing your request, please wait...
                </span>
              </p>
            ) : (
              state.status === "completed" && (
                <p className="flex items-start">
                  <span className="">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 448 512"
                      className="w-4 h-4 mr-2 mt-1 fill-green-500"
                    >
                      <path d="M438.6 105.4c12.5 12.5 12.5 32.8 0 45.3l-256 256c-12.5 12.5-32.8 12.5-45.3 0l-128-128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0L160 338.7 393.4 105.4c12.5-12.5 32.8-12.5 45.3 0z" />
                    </svg>
                  </span>
                  Your request has been completed for the request id{" "}
                  {state.request_id}
                </p>
              )
            )}
          </span>
        </div>
      </main>
    </div>
  );
};

export default App;
