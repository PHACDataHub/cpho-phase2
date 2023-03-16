import { render, screen } from '@testing-library/react';
import { Wordmark } from '../Wordmark'

describe('<Wordmark />', () => {

    it('renders an image', async () => {
        render(<Wordmark />)
        const image = await screen.findByRole('img')
        expect(image).toBeTruthy()
    })

    it('contains an alt-text aria-label', async () => {
        render(<Wordmark />)
        const image = await screen.findByRole('img')
        expect(image.getAttribute("aria-label")).toEqual("Canada Logo with Canadian flag - Logo du Canada avec Drapeau Canadien")
    })

    it('has preserve aspect ratio set', async () => {
        render(<Wordmark />)
        const image = await screen.findByRole('img')
        expect(image.getAttribute("preserveAspectRatio")).toEqual("xMinYMin meet")

    })

    // Width test section

    it('accepts a width prop', async () => {
        render(<Wordmark width={'10em'} />)
        const image = await screen.findByRole('img')
        expect(image.getAttribute('width')).toEqual('10em');
    });
    it('defaults to width of 20%', async () => {
        render(<Wordmark />)
        const image = await screen.findByRole('img')
        expect(image.getAttribute('width')).toEqual('20%')
    })

    // Color test section: this might be too coupled to the implementation, as we are testing the fill propoerty of the SVG path

    type TextColor = "black" | "white"

    it.each<TextColor>(["black", "white"])('textColor sets the text color: %n', async (desiredTextColor) => {
        render(<Wordmark textColor={desiredTextColor} />)

        const image = await screen.findByRole('img')

        const textColor = image.querySelector('path.fip_text')
        expect(textColor).not.toBe(null)
        if (textColor !== null) {
            expect(textColor.getAttribute('fill')).toEqual(desiredTextColor)
        }
    })


    // and now test the variant attribute affect the fill color of the flag
    it.each<TextColor>(["black", "white"])('monochrome variant renders flag same color as text: %n', async (desiredTextColor) => {
        render(<Wordmark textColor={desiredTextColor} variant="monochrome" />)

        const image = await screen.findByRole('img')

        const flagColor = image.querySelector('path.fip_flag')
        expect(flagColor).not.toBe(null)
        if (flagColor !== null) {
            expect(flagColor.getAttribute('fill')).toEqual(desiredTextColor)
        }
    })

    it.each<TextColor>(["black", "white"])('color variant always renders flag as red: %n', async (desiredTextColor) => {
        render(<Wordmark textColor={desiredTextColor} variant="color" />)

        const image = await screen.findByRole('img')

        const canadaRed = '#EA2D37';

        const flagColor = image.querySelector('path.fip_flag')
        expect(flagColor).not.toBe(null)
        if (flagColor !== null) {
            expect(flagColor.getAttribute('fill')).toEqual(canadaRed)
        }
    })

    // End of color section
})