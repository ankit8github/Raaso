import { test, expect, type APIRequestContext } from '@playwright/test'
import { execFileSync } from 'node:child_process'

const EVENT_ID = '10d01270-d650-442c-b80a-4adad80be594'

function resetE2EDatabase() {
  execFileSync(
    'python',
    ['run_e2e.py', '--reset'],
    {
      cwd: 'backend',
      stdio: 'inherit',
    },
  )
}

async function createCompatibleAttendee(
  request: APIRequestContext,
) {
  const userResponse = await request.post('/api/users', {
    data: {
      display_name: 'E2E Match Candidate',
      age_bracket: '21-25',
      city: 'Chandigarh',
      instagram_handle: '__e2e_match_candidate',
    },
  })

  expect(userResponse.ok()).toBeTruthy()

  const user = await userResponse.json()

  const attendanceResponse = await request.post('/api/attendances', {
    data: {
      user_id: user.id,
      event_id: EVENT_ID,
      intent: 'social_casual',
      dance_level: 'intermediate',
      vibes: 'traditional, high_energy',
      group_size_preference: 6,
    },
  })

  expect(attendanceResponse.ok()).toBeTruthy()

  return user
}

test.beforeEach(() => {
  resetE2EDatabase()
})

test('user can enter an event and reach matches', async ({ page }) => {
  await page.goto('/')

  await page.getByText('Raaso E2E Garba Night').click()
  await expect(page).toHaveURL(/\/events\/.*\/onboard$/)

  await page
    .getByRole('textbox', { name: 'e.g. Diya P.' })
    .fill('E2E Test User')

  await page
    .getByRole('textbox', { name: 'e.g. @diya_garba (for social' })
    .fill('__e2e_test_user')

  await page.getByText('Social & Casual').click()
  await page.getByText('Intermediate').click()

  await page
    .getByRole('button', { name: 'Find Compatible Matches &' })
    .click()

  await expect(page).toHaveURL('/matches')

  await expect(
    page.getByRole('heading', { name: 'Raaso E2E Garba Night' }),
  ).toBeVisible()

  await expect(
    page.getByText('Compatible Attendees (0)'),
  ).toBeVisible()

  await expect(page.getByText('No attendees yet')).toBeVisible()
})

test('compatible attendee appears in matches', async ({ page, request }) => {
  await createCompatibleAttendee(request)

  await page.goto('/')

  await page.getByText('Raaso E2E Garba Night').click()

  await page
    .getByRole('textbox', { name: 'e.g. Diya P.' })
    .fill('E2E Primary User')

  await page
    .getByRole('textbox', { name: 'e.g. @diya_garba (for social' })
    .fill('__e2e_primary_user')

  await page.getByText('Social & Casual').click()
  await page.getByText('Intermediate').click()

  await page
    .getByRole('button', { name: 'Find Compatible Matches &' })
    .click()

  await expect(page).toHaveURL('/matches')

  await expect(
    page.getByText('Compatible Attendees (1)'),
  ).toBeVisible()

  await expect(
    page.getByRole('heading', { name: 'E2E Match Candidate' }),
  ).toBeVisible()

  await expect(page.getByText('100%')).toBeVisible()

  await expect(
    page.getByText("Both share 'Social Casual' intent"),
  ).toBeVisible()

  await expect(
    page.getByText('Exact dance level match (Intermediate)'),
  ).toBeVisible()

  await expect(
    page.getByText('Shared vibes: High Energy, Traditional'),
  ).toBeVisible()

  await expect(
    page.getByText('Both prefer group size of 6'),
  ).toBeVisible()
})

test('user can create and leave a squad', async ({ page, request }) => {
  await page.goto('/')

  await page.getByText('Raaso E2E Garba Night').click()

  await page
    .getByRole('textbox', { name: 'e.g. Diya P.' })
    .fill('E2E Squad User')

  await page
    .getByRole('textbox', { name: 'e.g. @diya_garba (for social' })
    .fill('__e2e_squad_user')

  await page.getByText('Social & Casual').click()
  await page.getByText('Intermediate').click()

  await page
    .getByRole('button', { name: 'Find Compatible Matches &' })
    .click()

  await expect(page).toHaveURL('/matches')

  await page.getByRole('link', { name: 'View Squads' }).click()

  await expect(page).toHaveURL('/squads')

  await expect(
    page.getByRole('heading', { name: 'Raaso E2E Garba Night Squads' }),
  ).toBeVisible()

  await page.getByRole('button', { name: 'Create Squad' }).first().click()

  await page
    .getByPlaceholder('e.g. Baroda Raas Kings, Dandiya Queens')
    .fill('E2E Test Squad')


  await page
    .getByRole('button', { name: 'Create Squad', exact: true })
    .last()
    .click()

  await expect(
    page.getByRole('heading', { name: 'E2E Test Squad' }),
  ).toBeVisible()

  await expect(
    page.getByText('1 / 6 Members'),
  ).toBeVisible()

  await page.getByRole('button', { name: 'View Roster' }).click()

  await expect(
    page.getByRole('heading', { name: 'E2E Test Squad' }),
  ).toBeVisible()

  page.once('dialog', async (dialog) => {
    await dialog.accept()
  })

  await page.getByRole('button', { name: 'Leave Squad' }).click()

  const squadCard = page
    .locator('div.card')
    .filter({
      has: page.getByRole('heading', {
        name: 'E2E Test Squad',
        level: 4,
      }),
    })

  await expect(
    squadCard.getByText('0 / 6 Members'),
  ).toBeVisible()
})