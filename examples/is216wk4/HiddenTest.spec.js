import { describe, test, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import Ex1 from './src/components/Ex1.vue'
import Ex2 from './src/components/Ex2.vue'
import Ex3 from './src/components/Ex3.vue'
import Ex4 from './src/components/Ex4.vue'

describe('IS216 Week 4 hidden tests', () => {

  test('ex1_message', () => {
    const wrapper = mount(Ex1)
    expect(wrapper.text()).toContain('Choose your favorite fruit:')
  })

  test('ex1_fruits', () => {
    const wrapper = mount(Ex1)
    const text = wrapper.text().toLowerCase()
    expect(text).toContain('apple')
    expect(text).toContain('orange')
    expect(text).toContain('peach')
    expect(wrapper.findAll('input[type="radio"]')).toHaveLength(3)
  })

  test('ex2_first_image', () => {
    const wrapper = mount(Ex2)
    const images = wrapper.findAll('img')
    expect(images.length).toBeGreaterThanOrEqual(1)

    const first = images[0]
    expect(first.attributes('src')).toBe('/assets/me.png')
    expect(first.attributes('width')).toBe('200')
    expect(first.attributes('height')).toBe('200')
  })

  test('ex2_second_image', () => {
    const wrapper = mount(Ex2)
    const images = wrapper.findAll('img')
    expect(images.length).toBeGreaterThanOrEqual(2)

    const second = images[1]
    expect(second.attributes('src')).toBe('/assets/me.png')
    expect(second.attributes('width')).toBe('200')
    expect(second.attributes('height')).toBe('200')
  })

  test('ex3_username', async () => {
    const wrapper = mount(Ex3)
    const select = wrapper.find('select')

    expect(select.exists()).toBe(true)

    // Initial username state
    expect(wrapper.text()).toContain('Username')
    expect(wrapper.find('input').attributes('placeholder'))
      .toBe('Enter your username')

    // Must reactively switch away from username
    await select.setValue('Email login')
    expect(wrapper.text()).toContain('Email')
    expect(wrapper.find('input').attributes('placeholder'))
      .toBe('Enter your email address')

    // ...and back again
    await select.setValue('username')
    expect(wrapper.text()).toContain('Username')
    expect(wrapper.find('input').attributes('placeholder'))
      .toBe('Enter your username')
  })

  test('ex3_email', async () => {
    const wrapper = mount(Ex3)
    const select = wrapper.find('select')

    expect(select.exists()).toBe(true)

    await select.setValue('Email login')

    expect(wrapper.text()).toContain('Email')
    expect(wrapper.find('input').attributes('placeholder'))
      .toBe('Enter your email address')
  })

  test('ex4_initial', () => {
    const wrapper = mount(Ex4)

    const part1 = wrapper.find('#part1')
    const part2 = wrapper.find('#part2')

    const part1Inner = part1.find('div > div')
    const part2Inner = part2.find('div > div')

    expect(part1Inner.attributes('id')).toBe('demo')
    expect(part1Inner.classes()).toContain('blueBox')

    expect(part2Inner.attributes('id')).toBe('demo2')
    expect(part2Inner.attributes('style') || '').toContain('color: red')
  })

  test('ex4_color', async () => {
    const wrapper = mount(Ex4)
    const part1 = wrapper.find('#part1')
    const button = part1.find('button')
    const box = part1.find('div > div')

    expect(box.classes()).toContain('blueBox')
    expect(button.classes()).toContain('btn-primary')

    await button.trigger('click')

    expect(box.classes()).toContain('redBox')
    expect(button.classes()).toContain('btn-danger')
  })

  test('ex4_text_color', async () => {
    const wrapper = mount(Ex4)
    const part2 = wrapper.find('#part2')
    const button = part2.find('button')
    const box = part2.find('div > div')

    expect(box.attributes('style') || '').toContain('color: red')
    expect(button.classes()).toContain('btn-danger')

    await button.trigger('click')

    expect(box.attributes('style') || '').toContain('color: blue')
    expect(button.classes()).toContain('btn-primary')
  })

})
