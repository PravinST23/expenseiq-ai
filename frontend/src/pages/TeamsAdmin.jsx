import { useCallback, useEffect, useState } from 'react'
import { projectsApi, teamsApi } from '../api/resources'
import {
  Button,
  Card,
  EmptyState,
  ErrorBanner,
  Field,
  inputClass,
  Spinner,
} from '../components/ui'

const EMPTY_TEAM = { team_code: '', team_name: '' }
const EMPTY_PROJECT = {
  project_code: '',
  project_name: '',
  client_name: '',
  team_id: '',
}

export default function TeamsAdmin() {
  const [teams, setTeams] = useState(null)
  const [projects, setProjects] = useState(null)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const [teamForm, setTeamForm] = useState(EMPTY_TEAM)
  const [projectForm, setProjectForm] = useState(EMPTY_PROJECT)

  const load = useCallback(() => {
    Promise.all([teamsApi.list(), projectsApi.list()])
      .then(([teamList, projectList]) => {
        setTeams(teamList)
        setProjects(projectList)
        setProjectForm((f) => ({
          ...f,
          team_id: f.team_id || teamList[0]?.id || '',
        }))
      })
      .catch((err) => setError(err.message))
  }, [])

  useEffect(() => {
    load()
  }, [load])

  async function createTeam(event) {
    event.preventDefault()
    setBusy(true)
    setError(null)

    try {
      await teamsApi.create(teamForm)
      setTeamForm(EMPTY_TEAM)
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function createProject(event) {
    event.preventDefault()
    setBusy(true)
    setError(null)

    try {
      await projectsApi.create(projectForm)
      setProjectForm((f) => ({ ...EMPTY_PROJECT, team_id: f.team_id }))
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <h1 className="text-xl font-semibold text-slate-900">
        Teams &amp; Projects
      </h1>
      <p className="mt-1 text-sm text-slate-500">
        Manage MAC teams and the client projects that run under them.
        HR Head only.
      </p>

      <ErrorBanner message={error} />

      {teams === null ? (
        <Spinner />
      ) : (
        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Card className="p-5">
            <h2 className="text-sm font-semibold text-slate-900">
              MAC Teams ({teams.length})
            </h2>

            <form onSubmit={createTeam} className="mt-4 space-y-3">
              <Field label="Team Code">
                <input
                  className={inputClass}
                  placeholder="MAC9"
                  value={teamForm.team_code}
                  onChange={(e) =>
                    setTeamForm((f) => ({
                      ...f,
                      team_code: e.target.value,
                    }))
                  }
                  required
                />
              </Field>
              <Field label="Team Name">
                <input
                  className={inputClass}
                  placeholder="Cygnus"
                  value={teamForm.team_name}
                  onChange={(e) =>
                    setTeamForm((f) => ({
                      ...f,
                      team_name: e.target.value,
                    }))
                  }
                  required
                />
              </Field>
              <Button type="submit" disabled={busy} className="w-full">
                Add Team
              </Button>
            </form>

            {teams.length === 0 ? (
              <EmptyState title="No teams yet" />
            ) : (
              <ul className="mt-5 divide-y divide-slate-100">
                {teams.map((team) => (
                  <li
                    key={team.id}
                    className="flex items-center justify-between py-2 text-sm"
                  >
                    <span className="font-medium text-slate-900">
                      {team.team_code} - {team.team_name}
                    </span>
                    <span className="text-xs text-slate-500">
                      {team.employee_count} employees
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card className="p-5">
            <h2 className="text-sm font-semibold text-slate-900">
              Projects ({projects?.length ?? 0})
            </h2>

            <form onSubmit={createProject} className="mt-4 space-y-3">
              <Field label="Project Code">
                <input
                  className={inputClass}
                  placeholder="ACME"
                  value={projectForm.project_code}
                  onChange={(e) =>
                    setProjectForm((f) => ({
                      ...f,
                      project_code: e.target.value,
                    }))
                  }
                  required
                />
              </Field>
              <Field label="Project Name">
                <input
                  className={inputClass}
                  value={projectForm.project_name}
                  onChange={(e) =>
                    setProjectForm((f) => ({
                      ...f,
                      project_name: e.target.value,
                    }))
                  }
                  required
                />
              </Field>
              <Field label="Client Name">
                <input
                  className={inputClass}
                  value={projectForm.client_name}
                  onChange={(e) =>
                    setProjectForm((f) => ({
                      ...f,
                      client_name: e.target.value,
                    }))
                  }
                  required
                />
              </Field>
              <Field label="MAC Team">
                <select
                  className={inputClass}
                  value={projectForm.team_id}
                  onChange={(e) =>
                    setProjectForm((f) => ({
                      ...f,
                      team_id: e.target.value,
                    }))
                  }
                  required
                >
                  {teams.map((team) => (
                    <option key={team.id} value={team.id}>
                      {team.team_code} - {team.team_name}
                    </option>
                  ))}
                </select>
              </Field>
              <Button type="submit" disabled={busy} className="w-full">
                Add Project
              </Button>
            </form>

            {projects?.length === 0 ? (
              <EmptyState title="No projects yet" />
            ) : (
              <ul className="mt-5 divide-y divide-slate-100">
                {projects?.map((project) => (
                  <li key={project.id} className="py-2 text-sm">
                    <p className="font-medium text-slate-900">
                      {project.project_name} - {project.client_name}
                    </p>
                    <p className="text-xs text-slate-500">
                      {project.team_name ?? 'No team assigned'}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      )}
    </div>
  )
}
