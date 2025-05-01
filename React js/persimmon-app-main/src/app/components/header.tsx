// components/Header.tsx
import Link from 'next/link';
import styles from './Header.module.css';
import Image from 'next/image';

const Header: React.FC = () => {
  return (
    <header className={styles.header}>
      <Image src="images/logo.png" alt="Logo" className={styles.logo} />
      <h1 className={styles.title}>Persimmon</h1>
      <nav className={styles.nav}>
        <Link href="/" className={styles.navLink}>
          Home
        </Link>
        <Link href="/about" className={styles.navLink}>
          About Us
        </Link>
        <Link href="/contact" className={styles.navLink}>
          Contact Us
        </Link>
      </nav>
    </header>
  );
};

export default Header;
