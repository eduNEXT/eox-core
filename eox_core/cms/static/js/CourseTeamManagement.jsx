import React from 'react';
import {
  InputText, Button, StatusAlert, InputSelect,
} from '@edx/paragon';
import { clientRequest } from './client';
import LoadingIconComponent from './LoadingIcon';
/* eslint-disable import/no-unresolved */
import styles from '../css/CourseTeamManagement';


export default class CourseTeamManagement extends React.Component {
  constructor(props) {
    super(props);

    this.apiUrl = '/eox-core/management/course-team-management';
    this.organizationApiUrl = '/organizations';

    this.state = {
      org: '',
      user: '',
      isValid: false,
      openAlert: false,
      completedTasks: [],
      failedTasks: [],
      statusAlertMessage: 'Please, enter a valid data.',
      statusAlertType: 'warning',
      isLoading: false,
      orgList: [],
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.onCloseAlert = this.onCloseAlert.bind(this);
    this.emailValidator = this.emailValidator.bind(this);
  }

  componentDidMount() {
    this.getOrganizationList();
  }

  handleChange(value, name) {
    if (value !== name) {
      this.setState({
        [name]: value,
      });
    }
  }

  getOrganizationList() {
    this.setState({
      isLoading: true,
    });

    clientRequest(
      this.organizationApiUrl,
      'GET',
    ).then(
      res => this.handleResponse(res),
    ).then((response) => {
      this.fillOrganizationList(response);
    }).catch((error) => {
      this.openStatusAlert(`An error occurred while getting the organizations list: ${error.message}`, 'danger');
      this.setState({
        isLoading: false,
      });
    });
  }

  fillOrganizationList(response) {
    const organizationList = response;
    organizationList.unshift('');
    this.setState({
      orgList: organizationList,
      isLoading: false,
    });
  }

  handleSubmit(event, userRol) {
    event.preventDefault();

    if (!this.state.isValid || this.state.org === '') {
      this.openStatusAlert('Please, enter a valid data.', 'danger');
      return;
    }

    const methodType = (userRol !== '') ? 'POST' : 'DELETE';
    this.setState({
      completedTasks: [],
      failedTasks: [],
      isLoading: true,
    });

    clientRequest(
      this.apiUrl,
      methodType,
      {
        user: this.state.user,
        org: this.state.org,
        role: userRol,
      },
    ).then(
      res => res.json(),
    ).then((response) => {
      if (response.status !== 'Failed') {
        this.setStatsLog(response);
      } else {
        this.apiResponseError(response);
      }
    }).catch((error) => {
      console.log(error);
      this.setState({
        isLoading: false,
      });
    });
  }

  setStatsLog(response) {
    const actualCompletedTasks = response.complete_tasks.map((task) => {
      const message = `Task completed for ${task.course}`;
      return (
        <li key={task.course}>
          <p>
            {message}
          </p>
        </li>
      );
    });

    const actualFailedTasks = response.failed_tasks.map((task) => {
      const message = `Task was not completed for ${task.course} due to: ${task.message}`;
      return (
        <li key={task.course}>
          <p>
            {message}
          </p>
        </li>
      );
    });

    this.setState({
      completedTasks: actualCompletedTasks,
      failedTasks: actualFailedTasks,
      isLoading: false,
    });
  }

  apiResponseError(response) {
    this.openStatusAlert(response.message, 'danger');
    this.setState({
      isLoading: false,
    });
  }

  emailValidator(emailValue) {
    let feedback = { isValid: true };
    const emailRegEx = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if (!emailRegEx.test(emailValue)) {
      feedback = {
        isValid: false,
        validationMessage: 'Enter a valid user email.',
      };
      this.setState({
        isValid: false,
      });
    } else {
      this.setState({
        isValid: true,
      });
    }
    return feedback;
  }

  onCloseAlert() {
    this.setState({
      openAlert: false,
    });
  }

  openStatusAlert(message, type) {
    this.setState({
      openAlert: true,
      statusAlertMessage: message,
      statusAlertType: type,
    });
  }

  /* eslint-disable class-methods-use-this */
  handleResponse(response) {
    if (response.ok) {
      return response.json();
    }

    throw new Error(response.statusText);
  }

  render() {
    return (
      <div>
        <form onSubmit={this.handleSubmit}>
          <InputText
            description="The user email to apply the changes."
            id="username"
            isValid={false}
            label="User email:"
            name="user"
            onChange={this.handleChange}
            validator={this.emailValidator}
          />
          <InputSelect
            description="The org id to add/remove the user."
            id="org"
            label="Oranization name:"
            name="org"
            onChange={this.handleChange}
            options={this.state.orgList}
          />
          <Button
            className={['btn-primary']}
            label="Add as staff user."
            onClick={(event) => { this.handleSubmit(event, 'staff'); }}
          />
          <Button
            className={['btn-primary', styles.btnPrimarySpace]}
            label="Add as instructor user."
            onClick={(event) => { this.handleSubmit(event, 'instructor'); }}
          />
          <Button
            className={['btn-primary']}
            label="Remove user."
            onClick={(event) => { this.handleSubmit(event, ''); }}
          />
          <StatusAlert
            alertType={this.state.statusAlertType}
            dialog={this.state.statusAlertMessage}
            onClose={this.onCloseAlert}
            open={this.state.openAlert}
          />
        </form>
        <div>
          <h2>Operations complete:</h2>
          <ol>{this.state.completedTasks}</ol>
          <h2>Operations not complete:</h2>
          <ol>{this.state.failedTasks}</ol>
        </div>
        {this.state.isLoading && <LoadingIconComponent />}
      </div>
    );
  }
}
