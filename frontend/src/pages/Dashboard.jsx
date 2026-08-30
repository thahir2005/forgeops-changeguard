import { useState } from "react";
import { analyzePullRequest } from "../services/api";


function Dashboard() {
  const [owner, setOwner] = useState("thahir2005");
  const [repo, setRepo] = useState("forgeops-changeguard-demo");
  const [pullNumber, setPullNumber] = useState("1");

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  async function runAnalysis(event) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await analyzePullRequest({
        owner: owner.trim(),
        repo: repo.trim(),
        pull_number: Number(pullNumber),
      });

      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to analyze pull request."
      );
    } finally {
      setLoading(false);
    }
  }


  const analysis = result?.analysis;
  const risk = analysis?.risk;
  const blastRadius = analysis?.blast_radius;
  const pullRequest = result?.pull_request;


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
              Analyze a GitHub pull request before
              changes reach production.
            </p>


            <form
              className="pr-form"
              onSubmit={runAnalysis}
            >
              <input
                type="text"
                placeholder="Owner"
                value={owner}
                onChange={(event) =>
                  setOwner(event.target.value)
                }
                aria-label="GitHub owner"
                required
              />

              <input
                type="text"
                placeholder="Repository"
                value={repo}
                onChange={(event) =>
                  setRepo(event.target.value)
                }
                aria-label="GitHub repository"
                required
              />

              <input
                type="number"
                min="1"
                placeholder="PR #"
                value={pullNumber}
                onChange={(event) =>
                  setPullNumber(event.target.value)
                }
                aria-label="Pull request number"
                required
              />

              <button
                className="analyze-button"
                type="submit"
                disabled={loading}
              >
                {loading
                  ? "Analyzing..."
                  : "Analyze PR"}
              </button>
            </form>

          </div>

        </section>


        {error && (
          <div className="error">
            {error}
          </div>
        )}


        {pullRequest && (
          <section className="panel">

            <div className="pr-summary">

              <div>
                <p className="eyebrow">
                  PULL REQUEST
                </p>

                <h3>
                  #{pullRequest.number}{" "}
                  {pullRequest.title}
                </h3>

                <p className="description">
                  {result.repository}
                </p>
              </div>


              <div className="pr-meta">

                <span>
                  {pullRequest.head_branch}
                  {" → "}
                  {pullRequest.base_branch}
                </span>

                <span>
                  {pullRequest.author}
                </span>

                <a
                  href={pullRequest.url}
                  target="_blank"
                  rel="noreferrer"
                >
                  View PR
                </a>

              </div>

            </div>

          </section>
        )}


        {risk && (
          <>

            <section className="risk-section">

              <div className="risk-card">
                <p>OVERALL RISK</p>

                <div className="risk-score">
                  {risk.overall_score}
                  <span>/100</span>
                </div>

                <strong>
                  {risk.category.toUpperCase()}
                </strong>
              </div>


              <div className="metric">
                <span>Reliability</span>

                <strong>
                  {risk.reliability_score}
                </strong>
              </div>


              <div className="metric">
                <span>Security</span>

                <strong>
                  {risk.security_score}
                </strong>
              </div>


              <div className="metric">
                <span>Cost</span>

                <strong>
                  {risk.cost_score}
                </strong>
              </div>

            </section>


            {blastRadius && (
              <section className="panel">

                <div className="panel-header">

                  <div>
                    <p className="eyebrow">
                      DEPENDENCY ANALYSIS
                    </p>

                    <h3>
                      Blast Radius
                    </h3>
                  </div>

                  <span>
                    {blastRadius.blast_radius_count}{" "}
                    {blastRadius.blast_radius_count === 1
                      ? "service"
                      : "services"}
                  </span>

                </div>


                <div className="impact-grid">

                  <div className="impact-column">
                    <h4>
                      Directly Affected
                    </h4>

                    {blastRadius
                      .directly_affected_services
                      .length > 0 ? (
                        blastRadius
                          .directly_affected_services
                          .map((service) => (
                            <div
                              className="impact-item"
                              key={service}
                            >
                              {service}
                            </div>
                          ))
                      ) : (
                        <div className="impact-item">
                          No direct impact
                        </div>
                      )}
                  </div>


                  <div className="impact-column">
                    <h4>
                      Transitively Affected
                    </h4>

                    {blastRadius
                      .transitively_affected_services
                      .length > 0 ? (
                        blastRadius
                          .transitively_affected_services
                          .map((service) => (
                            <div
                              className="impact-item"
                              key={service}
                            >
                              {service}
                            </div>
                          ))
                      ) : (
                        <div className="impact-item">
                          No transitive impact
                        </div>
                      )}
                  </div>

                </div>


                <div className="dependencies">

                  <h4>
                    Discovered Dependencies
                  </h4>

                  {blastRadius.dependencies.length > 0 ? (
                    blastRadius.dependencies.map(
                      (dependency, index) => (
                        <div
                          className="dependency"
                          key={`${dependency.service}-${dependency.dependency}-${index}`}
                        >
                          <strong>
                            {dependency.service}
                          </strong>

                          <span>→</span>

                          <strong>
                            {dependency.dependency}
                          </strong>

                          <small>
                            {dependency.source}
                          </small>
                        </div>
                      )
                    )
                  ) : (
                    <p>
                      No explicit dependencies discovered.
                    </p>
                  )}

                </div>

              </section>
            )}


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
                  {analysis.files_changed} files
                </span>

              </div>


              <div className="file-list">

                {analysis.files.map(
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

                <span>
                  {risk.reasons.length} factors
                </span>

              </div>


              <div className="reasons">

                {risk.reasons.map(
                  (reason, index) => (
                    <div
                      className="reason"
                      key={`${reason}-${index}`}
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
