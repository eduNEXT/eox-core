import React from 'react';
import styles from '../css/LoadingIcon'


export function LoadingIconComponent(props) {
    const spinnerStyles = `fa fa-spinner fa-5x ${styles.courseManagementSpinner}`;
    return <div className={styles.courseManagementSpinnerContainer}>
        <i className={spinnerStyles} aria-hidden="true"></i>
    </div>
}
