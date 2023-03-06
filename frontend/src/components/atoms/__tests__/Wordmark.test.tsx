import React from 'react'
import { screen, render } from '@testing-library/react'
import { Wordmark } from '../Wordmark'
describe('<Wordmark />', () => {
    // afterEach(() => flush())
    it('renders an accessible svg image', async () => {
        render(<Wordmark />)
        const image = await screen.findByRole('img')
        expect(image).toBeTruthy()
    })
    it('accepts a width prop', async () => {
        render(<Wordmark width="1000%" />)
        const image = await screen.findByRole('img')
        expect(image.getAttribute('width')).toEqual('1000%')
    })
    it('defaults to width of 10em', async () => {
        render(<Wordmark />)
        const image = await screen.findByRole('img')
        expect(image.getAttribute('width')).toEqual('10em')
    })
    // it('allows the flag colour to be set', () => {
    //     render(<Wordmark flag="#fff" />)
    // console.log({sheet: sheet.tags})
    //     expect(stringify(sheet)).toMatch(/fill:#fff/)
    // })
    //
    //  it('allows the text colour to be set', () => {
    //    render(<WordMark text="#ddd" />)
    //    expect(stringify(sheet)).toMatch(/fill:#ddd/)
    //  })
    //
    //  it('allows passing through abritrary props', () => {
    //    let wrapper = render(<WordMark focusable="false" whizz="bang" />)
    //    expect(wrapper.props().focusable).toEqual('false')
    //    expect(wrapper.props().whizz).toEqual('bang')
    //  })
})