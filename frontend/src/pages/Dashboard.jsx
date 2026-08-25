import { useState } from "react";
import { analyzeChange } from "../services/api";


const examplePayload = {
  changed_files: [
    "infrastructure/terraform/main.tf",
    "infrastructure/kubernetes/deployment.yaml",
  ],

  diffs: {
    "infrastructure/terraform/main.tf": `--- a/infrastructure/terraform/main.tf
+++ b/infrastructure/terraform/main.tf
@@ -10,7 +10,7 @@
 resource "aws_instance" "app" {
-  instance_type = "t3.medium"
+  instance_type = "t3.2xlarge"
 }`,

    "infrastructure/kubernetes/deployment.yaml": `--- a/infrastructure/kubernetes/deployment.yaml
+++ b/infrastructure/kubernetes/deployment.yaml
@@ -10,7 +10,7 @@
 spec:
-  replicas: 3
+  replicas: 1`,
  },
};


function Dashboard() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  async function runAnalysis() {
    setLoading(true);
    setError("");

    try {
      const data = await analyzeChange(
        examplePayload
      );

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }


  return (
    <div className="dashboard">

      <header className="topbar">
        <div>
          <h1>ForgeOps</h1>
          <span>ChangeGuard</span>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          System Online
        </div>
      </header>


      <main className="content">

        <section className="hero">
          <div>
            <p className="eyebrow">
              CHANGE INTELLIGENCE
            </p>

            <h2>
              Understand the impact
              before deployment.
            </h2>

            <p className="description">
              Analyze infrastructure and
              application changes before
              they reach production.
            </p>
          </div>

          <button
            className="analyze-button"
            onClick={runAnalysis}
            disabled={loading}
          >
            {loading
              ? "Analyzing..."
              : "Analyze Change"}
          </button>
        </section>


        {error && (
          <div className="error">
            {error}
          </div>
        )}


        {result && (
          <>

            <section className="risk-section">

              <div className="risk-card">
                <p>OVERALL RISK</p>

                <div className="risk-score">
                  {result.risk.overall_score}
                  <span>/100</span>
                </div>

                <strong>
                  {result.risk.category.toUpperCase()}
                </strong>
              </div>


              <div className="metric">
                <span>Reliability</span>
                <strong>
                  {result.risk.reliability_score}
                </strong>
              </div>


              <div className="metric">
                <span>Security</span>
                <strong>
                  {result.risk.security_score}
                </strong>
              </div>


              <div className="metric">
                <span>Cost</span>
                <strong>
                  {result.risk.cost_score}
                </strong>
              </div>

            </section>


            <section className="panel">

              <div className="panel-header">
                <div>
                  <p className="eyebrow">
                    CHANGE ANALYSIS
                  </p>

                  <h3>
                    Changed Files
                  </h3>
                </div>

                <span>
                  {result.files_changed} files
                </span>
              </div>


              <div className="file-list">

                {result.files.map(
                  (file) => (
                    <div
                      className="file"
                      key={file.file}
                    >
                      <div>
                        <strong>
                          {file.file}
                        </strong>

                        <span>
                          {file.change_type}
                        </span>
                      </div>

                      <div className="diff-count">
                        <span>
                          +{file.added_lines.length}
                        </span>

                        <span>
                          -{file.removed_lines.length}
                        </span>
                      </div>
                    </div>
                  )
                )}

              </div>

            </section>


            <section className="panel">

              <div className="panel-header">

                <div>
                  <p className="eyebrow">
                    WHY?
                  </p>

                  <h3>
                    Risk Factors
                  </h3>
                </div>

              </div>


              <div className="reasons">

                {result.risk.reasons.map(
                  (reason, index) => (
                    <div
                      className="reason"
                      key={index}
                    >
                      <span>!</span>
                      <p>{reason}</p>
                    </div>
                  )
                )}

              </div>

            </section>

          </>
        )}

      </main>

    </div>
  );
}


export default Dashboard;
