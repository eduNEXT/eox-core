import React from 'react';
/* eslint-disable import/no-unresolved */
import styles from '../css/LoadingIcon';


/* eslint-disable no-unused-vars */
export default function LoadingIconComponent(props) {
  const spinnerStyles = `fa fa-spinner fa-5x ${styles.courseManagementSpinner}`;
  return (
    <div className={styles.courseManagementSpinnerContainer}>
      <i aria-hidden="true" className={spinnerStyles} />
    </div>
  );
}
