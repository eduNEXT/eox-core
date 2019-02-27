import React from 'react';
import ReactDOM from 'react-dom';
import { Tabs } from '@edx/paragon';
import PropTypes from 'prop-types';
import CourseTeamManagement from './CourseTeamManagement';
import CourseSettings from './CourseSettings';

function CourseManagement(props) {
  return (
    <Tabs labels={['Course team management', 'Course settings', 'Panel 3']}>
      <div>
        <CourseTeamManagement />
      </div>
      <div>
        <CourseSettings
          courseKey={props.courseSettings.course_key}
          detailsFields={props.courseSettings.details_fields}
          requestTimeOut={props.courseSettings.request_timeout_value}
        />
      </div>
      <div>
        Panel 3
      </div>
    </Tabs>
  );
}

/* eslint-disable import/prefer-default-export */
export class RenderReactComponent {
  constructor(properties = {}) {
    Object.assign(this, {
      properties,
    });
    this.renderReact();
  }

  renderReact() {
    ReactDOM.render(
      React.createElement(CourseManagement, this.properties, null),
      /* eslint-disable no-undef */
      document.getElementById('root'),
    );
  }
}

CourseManagement.defaultProps = {
  courseSettings: {
    course_key: '',
    details_fields: [],
    request_timeout_value: 500,
  },
};

CourseManagement.propTypes = {
  courseSettings: PropTypes.shape({
    course_key: PropTypes.string,
    details_fields: PropTypes.arrayOf(PropTypes.string),
    request_timeout_value: PropTypes.number,
  }),
};
