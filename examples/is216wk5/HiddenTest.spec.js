import { describe, test, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import Ex1 from './src/components/Ex1.vue'
import Ex2 from './src/components/Ex2.vue'
import Ex3 from './src/components/Ex3.vue'
import Ex4 from './src/components/Ex4.vue'

describe('IS216 Week 5 hidden tests', () => {

  test('ex1_over', async () => {
    const wrapper = mount(Ex1)
    const target = wrapper.find('div')
    expect(target.attributes('id')).toBe('circle')
    await target.trigger('mouseover')
    expect(target.attributes('id')).toBe('square')
  })

  test('ex1_out', async () => {
    const wrapper = mount(Ex1)
    const target = wrapper.find('div')
    await target.trigger('mouseover')
    expect(target.attributes('id')).toBe('square')
    await target.trigger('mouseout')
    expect(target.attributes('id')).toBe('circle')
  })

  test('ex2_buttons', async () => {
    const wrapper = mount(Ex2)
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBeGreaterThanOrEqual(3)
    const text = () => wrapper.text()
    expect(text()).toContain('Current: 0 - 0')
    await buttons[0].trigger('click')
    expect(text()).toContain('Current: 1 - 0')
    await buttons[1].trigger('click')
    expect(text()).toContain('Current: 1 - 1')
  })

  test('ex2_expressions', async () => {
    const wrapper = mount(Ex2)
    const buttons = wrapper.findAll('button')
    const text = () => wrapper.text().replace(/\s+/g, ' ')
    expect(text()).toContain('Total points: 0')
    expect(text()).toContain('Points left to win: 10')
    await buttons[0].trigger('click')
    await buttons[0].trigger('click')
    await buttons[1].trigger('click')
    expect(text()).toContain('Total points: 3')
    expect(text()).toContain('Points left to win: 8')
  })

  test('ex2_status_reset', async () => {
    const wrapper = mount(Ex2)
    const buttons = wrapper.findAll('button')
    const text = () => wrapper.text().replace(/\s+/g, ' ')
    expect(text()).toContain('No winner yet. Keep playing!')
    for (let i = 0; i < 10; i++) {
      await buttons[0].trigger('click')
    }
    expect(text()).toContain('Winner: FALCONS')
    await buttons[2].trigger('click')
    expect(text()).toContain('Current: 0 - 0')
    expect(text()).toContain('No winner yet. Keep playing!')
  })

  test('ex3_add_subtract', async () => {
    const wrapper = mount(Ex3)
    const inputs = wrapper.findAll('input')
    const select = wrapper.find('select')
    expect(inputs.length).toBeGreaterThanOrEqual(2)
    expect(select.exists()).toBe(true)
    await inputs[0].setValue('12')
    await inputs[1].setValue('5')
    await select.setValue('+')
    expect(wrapper.text()).toContain('= 17')
    await select.setValue('-')
    expect(wrapper.text()).toContain('= 7')
  })

  test('ex3_other_ops', async () => {
    const wrapper = mount(Ex3)
    const inputs = wrapper.findAll('input')
    const select = wrapper.find('select')
    await inputs[0].setValue('12')
    await inputs[1].setValue('5')
    await select.setValue('*')
    expect(wrapper.text()).toContain('= 60')
    await select.setValue('/')
    expect(wrapper.text()).toContain('= 2.4')
    await select.setValue('%')
    expect(wrapper.text()).toContain('= 2')
  })

  test('ex4_initial', () => {
    const wrapper = mount(Ex4)
    const items = wrapper.findAll('li')
    expect(items).toHaveLength(5)
    const text = wrapper.text().toLowerCase()
    expect(text).toContain('keyboard')
    expect(text).toContain('mouse')
    expect(text).toContain('iphone')
    expect(text).toContain('macbook')
    expect(text).toContain('adapter')
  })

  test('ex4_add_button', async () => {
    const wrapper = mount(Ex4)
    const input = wrapper.find('input')
    const buttons = wrapper.findAll('button')
    expect(input.exists()).toBe(true)
    await input.setValue('webcam')
    const addButton = buttons.find(
      button => button.text().toLowerCase().includes('add')
    )
    expect(addButton).toBeTruthy()
    await addButton.trigger('click')
    expect(wrapper.text().toLowerCase()).toContain('webcam')
  })

  test('ex4_add_enter', async () => {
    const wrapper = mount(Ex4)
    const input = wrapper.find('input')
    expect(input.exists()).toBe(true)
    await input.setValue('speaker')
    await input.trigger('keyup', { key: 'Enter' })
    expect(wrapper.text().toLowerCase()).toContain('speaker')
  })

  test('ex4_delete', async () => {
    const wrapper = mount(Ex4)
    expect(wrapper.findAll('li')).toHaveLength(5)
    const deleteButtons = wrapper.findAll('li button')
    expect(deleteButtons.length).toBeGreaterThanOrEqual(1)
    await deleteButtons[0].trigger('click')
    expect(wrapper.findAll('li')).toHaveLength(4)
    expect(wrapper.text().toLowerCase()).not.toContain('keyboard')
  })

})
