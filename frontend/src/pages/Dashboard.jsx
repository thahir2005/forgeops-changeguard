import { useState } from "react";
import { analyzePullRequest } from "../services/api";


function Dashboard() {
  const [prUrl, setPrUrl] = useState(
    "https://github.com/thahir2005/forgeops-changeguard-demo/pull/1"
  );

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  async function runAnalysis(event) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const match = prUrl.trim().match(
        /^https?:\/\/github\.com\/([^/]+)\/([^/]+)\/pull\/(\d+)\/?$/
      );

      if (!match) {
        throw new Error(
          "Enter a valid GitHub pull request URL."
        );
      }

      const [, parsedOwner, parsedRepo, parsedPullNumber] = match;

      const data = await analyzePullRequest({
        owner: parsedOwner,
        repo: parsedRepo,
        pull_number: Number(parsedPullNumber),
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
                type="url"
                placeholder="https://github.com/owner/repository/pull/123"
                value={prUrl}
                onChange={(event) =>
                  setPrUrl(event.target.value)
                }
                aria-label="GitHub pull request URL"
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


            <section
              className={`panel decision-card decision-${risk.decision}`}
            >

              <div>
                <p className="eyebrow">
                  DEPLOYMENT DECISION
                </p>

                <h3>
                  {risk.decision_label}
                </h3>

                <span>
                  {risk.decision_message}
                </span>
              </div>

              <div className="decision-score">
                <span>Risk Score</span>
                <strong>{risk.overall_score}/100</strong>
              </div>

            </section>


            {risk.risk_breakdown && (
              <section className="panel">

                <div className="panel-header">

                  <div>
                    <p className="eyebrow">
                      RISK BREAKDOWN
                    </p>

                    <h3>
                      Weighted Risk Factors
                    </h3>
                  </div>

                  <span>
                    {risk.risk_breakdown.length} factors
                  </span>

                </div>


                <div className="risk-breakdown">

                  {risk.risk_breakdown.map(
                    (item) => (
                      <div
                        className="risk-breakdown-item"
                        key={item.factor}
                      >

                        <div className="risk-breakdown-main">

                          <div>
                            <strong>
                              {item.factor}
                            </strong>

                            <span>
                              {Math.round(item.weight * 100)}% weight
                            </span>
                          </div>

                          <strong>
                            {item.contribution}
                          </strong>

                        </div>


                        <div className="risk-breakdown-bar">

                          <div
                            className="risk-breakdown-fill"
                            style={{
                              width: `${item.score}%`,
                            }}
                          />

                        </div>


                        <div className="risk-breakdown-meta">
                          <span>
                            Score: {item.score}/100
                          </span>

                          <span>
                            Contribution: {item.contribution}
                          </span>
                        </div>

                      </div>
                    )
                  )}

                </div>

              </section>
            )}


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


                        {analysis.recommendations &&
              analysis.recommendations.length > 0 && (
                <section className="panel">

                  <div className="panel-header">

                    <div>
                      <p className="eyebrow">
                        RECOMMENDATIONS
                      </p>

                      <h3>
                        Recommended Actions
                      </h3>
                    </div>

                    <span>
                      {analysis.recommendations.length} actions
                    </span>

                  </div>


                  <div className="recommendations">

                    {analysis.recommendations.map(
                      (recommendation, index) => (
                        <div
                          className="recommendation"
                          key={`${recommendation}-${index}`}
                        >

                          <span>
                            {String(index + 1).padStart(2, "0")}
                          </span>

                          <p>
                            {recommendation}
                          </p>

                        </div>
                      )
                    )}

                  </div>

                </section>
              )}

          </>
        )}

      </main>

    </div>
  );
}


export default Dashboard;
