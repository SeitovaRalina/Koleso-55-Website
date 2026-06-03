import Hero from '../components/home/Hero'
import WeeklyEvents from '../components/home/WeeklyEvents'
import HowItWorks from '../components/home/HowItWorks'
import Reviews from '../components/home/Reviews'
import GiftCertificates from '../components/home/GiftCertificates'
import CustomRequest from '../components/home/CustomRequest'

export default function Home() {
    return (
        <>
            <Hero />
            <WeeklyEvents />
            <HowItWorks />
            <Reviews />
            <GiftCertificates />
            <CustomRequest />
        </>
    )
}
